import os
import logging
import asyncio
import json
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load env variables and setup logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OrbaDesktop.Gateway")

# Import our backend agent and tool metadata
from agent import OrbaAgent
from tools import TOOL_METADATA

# Global dictionary to track Telegram approvals
tg_pending_approvals = {}

class TelegramGateway:
    def __init__(self):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.agent = OrbaAgent()
        self.provider = "ollama" # Default to local Ollama
        self.model = "gemma"

    async def start(self):
        if not self.token:
            logger.warning("TELEGRAM_BOT_TOKEN non configuré. Le gateway Telegram ne démarrera pas.")
            return

        # Build application
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("model", self.model_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_approval_callback))

        # Start polling
        logger.info("Démarrage du Gateway Telegram...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔮 *Bienvenue sur Orba OS Desktop Gateway!*\n\n"
            "Je suis Orba, ton assistant souverain connecté à ton ordinateur.\n"
            "Tu peux me parler par écrit ou me demander de piloter des outils locaux.\n\n"
            "Commandes utiles :\n"
            "/start - Revoir ce message\n"
            "/model [provider:model] - Changer de modèle (ex: `/model gemini:gemini-1.5-flash`)",
            parse_mode="Markdown"
        )

    async def model_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                f"Modèle actuel : `{self.provider}:{self.model}`\n"
                "Pour changer, utilise : `/model provider:model` (ex: `/model gemini:gemini-1.5-flash`)",
                parse_mode="Markdown"
            )
            return

        try:
            arg = context.args[0]
            prov, mod = arg.split(":")
            self.provider = prov
            self.model = mod
            await update.message.reply_text(f"✅ Modèle configuré sur `{self.provider}:{self.model}`", parse_mode="Markdown")
        except Exception:
            await update.message.reply_text("❌ Syntaxe invalide. Exemple : `/model ollama:gemma` ou `/model gemini:gemini-1.5-flash`")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        # Start ReAct agent loop
        current_prompt = user_text
        max_turns = 3
        
        for turn in range(max_turns):
            try:
                # Inférence LLM
                raw_response = await asyncio.to_thread(self.agent.query_llm, current_prompt, self.provider, self.model)
                logger.info(f"Telegram Gateway LLM response: {raw_response}")
                
                start_idx = raw_response.find('{')
                end_idx = raw_response.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_part = raw_response[start_idx:end_idx + 1]
                    response_json = json.loads(json_part)
                else:
                    raise ValueError("Format JSON invalide")
                
                thought = response_json.get("thought", "")
                tool_name = response_json.get("tool", "none")
                parameters = response_json.get("parameters", {})
                reply = response_json.get("reply", "")
                
                if thought:
                    logger.info(f"Thought: {thought}")
                
                if tool_name == "none" or not tool_name:
                    if reply:
                        await update.message.reply_text(reply)
                    break
                
                # Executing system tools
                if tool_name in TOOL_METADATA:
                    meta = TOOL_METADATA[tool_name]
                    category = meta.get("category", "SAFE")
                    desc = meta.get("desc", "")
                    
                    if category == "CRITICAL":
                        # Require inline keyboard approval
                        action_id = str(uuid.uuid4())
                        keyboard = [
                            [
                                InlineKeyboardButton("✅ Approuver", callback_data=f"approve_{action_id}"),
                                InlineKeyboardButton("❌ Refuser", callback_data=f"reject_{action_id}")
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"⚠️ *Alerte de Sécurité Orba OS*\n"
                            f"L'assistant souhaite exécuter une action critique sur votre PC :\n\n"
                            f"• *Outil* : `{tool_name}` ({desc})\n"
                            f"• *Paramètres* : `{json.dumps(parameters)}`\n\n"
                            f"Veuillez approuver ou refuser cette action.",
                            reply_markup=reply_markup,
                            parse_mode="Markdown"
                        )
                        
                        # Wait for inline click
                        future = asyncio.get_running_loop().create_future()
                        tg_pending_approvals[action_id] = (future, tool_name, parameters)
                        
                        try:
                            # Wait up to 60s
                            approved = await asyncio.wait_for(future, timeout=60.0)
                            if approved:
                                await update.message.reply_text("🔄 Action autorisée. Exécution...")
                                tool_output = await asyncio.to_thread(self.agent.run_tool, tool_name, parameters)
                                current_prompt = f"Résultat de l'outil {tool_name} : {tool_output}\n\nRéponds maintenant à l'utilisateur."
                            else:
                                await update.message.reply_text("🚫 Action refusée. Annulation.")
                                break
                        except asyncio.TimeoutError:
                            await update.message.reply_text("⏰ Temps d'approbation écoulé. Action annulée.")
                            if action_id in tg_pending_approvals:
                                del tg_pending_approvals[action_id]
                            break
                    else:
                        # Safe tool, execute directly
                        await update.message.reply_text(f"⚙️ Exécution de `{tool_name}`...")
                        tool_output = await asyncio.to_thread(self.agent.run_tool, tool_name, parameters)
                        current_prompt = f"Résultat de l'outil {tool_name} : {tool_output}\n\nRéponds maintenant à l'utilisateur."
                else:
                    await update.message.reply_text(f"❌ Outil `{tool_name}` inconnu.")
                    break
                    
            except json.JSONDecodeError:
                await update.message.reply_text(raw_response)
                break
            except Exception as e:
                logger.error(f"Error in Telegram agent loop: {e}")
                await update.message.reply_text(f"❌ Une erreur est survenue : {str(e)}")
                break

    async def handle_approval_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith("approve_") or data.startswith("reject_"):
            approved = data.startswith("approve_")
            action_id = data.split("_")[1]
            
            if action_id in tg_pending_approvals:
                future, _, _ = tg_pending_approvals[action_id]
                if not future.done():
                    future.set_result(approved)
                
                # Edit markup to show resolution
                status_text = "✅ Action Approuvée" if approved else "❌ Action Refusée"
                await query.edit_message_reply_markup(reply_markup=None)
                await query.edit_message_text(text=query.message.text + f"\n\n*Statut : {status_text}*", parse_mode="Markdown")
                del tg_pending_approvals[action_id]

async def main():
    gateway = TelegramGateway()
    await gateway.start()
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    if "TELEGRAM_BOT_TOKEN" in os.environ and os.environ["TELEGRAM_BOT_TOKEN"]:
        asyncio.run(main())
    else:
        print("TELEGRAM_BOT_TOKEN n'est pas défini dans l'environnement. Le gateway n'a pas pu démarrer.")
