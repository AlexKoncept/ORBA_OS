import os
import json
import logging
import asyncio
import uuid
from fastapi import APIRouter, Form, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Import agent and tools
from agent import OrbaAgent
from tools import TOOL_METADATA

logger = logging.getLogger("OrbaDesktop.WhatsApp")

whatsapp_router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Gateway"])

# Global dictionary for WhatsApp approvals
# Maps action_id -> (Future, tool_name, parameters)
wa_pending_approvals = {}

# Twilio Client Initialization helper
def get_twilio_client():
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    if account_sid and auth_token:
        return Client(account_sid, auth_token)
    return None

def send_wa_message(to_number: str, text: str):
    """Send an outbound WhatsApp message using Twilio API."""
    client = get_twilio_client()
    from_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    if client:
        try:
            client.messages.create(
                body=text,
                from_=from_number,
                to=to_number
            )
            logger.info(f"WhatsApp sent to {to_number}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
    else:
        logger.warning("Twilio client non configuré. Impossible d'envoyer le message WhatsApp.")

@whatsapp_router.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    """Webhook endpoint for Twilio WhatsApp incoming messages."""
    user_text = Body.strip()
    sender = From # Format: whatsapp:+33612345678
    
    logger.info(f"WhatsApp message from {sender}: {user_text}")
    
    # 1. Check if this is an approval response (e.g. "OUI action_id" or "NON action_id")
    cleaned_text = user_text.upper()
    if cleaned_text.startswith("OUI") or cleaned_text.startswith("NON"):
        parts = cleaned_text.split()
        if len(parts) >= 2:
            decision = parts[0] == "OUI"
            action_id = parts[1].lower()
            
            if action_id in wa_pending_approvals:
                future, _, _ = wa_pending_approvals[action_id]
                if not future.done():
                    future.set_result(decision)
                
                resp = MessagingResponse()
                resp.message(f"✅ Décision enregistrée ({'Autorisé' if decision else 'Refusé'}). Exécution en cours...")
                return Response(content=str(resp), media_type="application/xml")
            
    # 2. Otherwise, treat it as a standard agent query
    # Instanciating agent
    agent = OrbaAgent()
    provider = "ollama" # Default
    model = "gemma"
    
    # We run the ReAct agent loop asynchronously
    asyncio.create_task(run_whatsapp_agent_loop(agent, sender, user_text, provider, model))
    
    # Return an empty response immediately to avoid Twilio timeout
    resp = MessagingResponse()
    return Response(content=str(resp), media_type="application/xml")

async def run_whatsapp_agent_loop(agent: OrbaAgent, sender: str, user_text: str, provider: str, model: str):
    current_prompt = user_text
    max_turns = 3
    
    # Send a typing/thinking notification
    send_wa_message(sender, "⏳ Orba réfléchit...")
    
    for turn in range(max_turns):
        try:
            # Query LLM
            raw_response = await asyncio.to_thread(agent.query_llm, current_prompt, provider, model)
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_part = raw_response[start_idx:end_idx + 1]
                response_json = json.loads(json_part)
            else:
                raise ValueError("Format JSON invalide")
            
            tool_name = response_json.get("tool", "none")
            parameters = response_json.get("parameters", {})
            reply = response_json.get("reply", "")
            
            if tool_name == "none" or not tool_name:
                if reply:
                    send_wa_message(sender, reply)
                break
                
            # Execute tool
            if tool_name in TOOL_METADATA:
                meta = TOOL_METADATA[tool_name]
                category = meta.get("category", "SAFE")
                desc = meta.get("desc", "")
                
                if category == "CRITICAL":
                    action_id = str(uuid.uuid4())[:8] # Shorten UUID for easy typing on phone
                    
                    send_wa_message(
                        sender,
                        f"⚠️ *Alerte de Sécurité Orba OS*\n"
                        f"L'assistant souhaite exécuter une action critique sur votre PC :\n\n"
                        f"• *Outil* : {tool_name} ({desc})\n"
                        f"• *Paramètres* : {json.dumps(parameters)}\n\n"
                        f"Répondez par :\n"
                        f"👉 *OUI {action_id}* pour autoriser\n"
                        f"👉 *NON {action_id}* pour refuser"
                    )
                    
                    future = asyncio.get_running_loop().create_future()
                    wa_pending_approvals[action_id] = (future, tool_name, parameters)
                    
                    timeout_val = float(os.environ.get("ORBA_APPROVAL_TIMEOUT", "60.0"))
                    try:
                        approved = await asyncio.wait_for(future, timeout=timeout_val)
                        if approved:
                            send_wa_message(sender, "🔄 Action approuvée. Exécution en cours...")
                            tool_output = await asyncio.to_thread(agent.run_tool, tool_name, parameters)
                            current_prompt = f"Résultat de l'outil {tool_name} : {tool_output}\n\nRéponds maintenant à l'utilisateur."
                        else:
                            send_wa_message(sender, "🚫 Action rejetée. Annulation.")
                            break
                    except asyncio.TimeoutError:
                        send_wa_message(sender, "⏰ Temps d'approbation écoulé. Action annulée.")
                        if action_id in wa_pending_approvals:
                            del wa_pending_approvals[action_id]
                        break
                else:
                    # Safe tool
                    send_wa_message(sender, f"⚙️ Exécution de {tool_name}...")
                    tool_output = await asyncio.to_thread(agent.run_tool, tool_name, parameters)
                    current_prompt = f"Résultat de l'outil {tool_name} : {tool_output}\n\nRéponds maintenant à l'utilisateur."
            else:
                send_wa_message(sender, f"❌ Outil {tool_name} inconnu.")
                break
                
        except json.JSONDecodeError:
            send_wa_message(sender, raw_response)
            break
        except Exception as e:
            logger.error(f"Error in WhatsApp agent loop: {e}")
            send_wa_message(sender, f"❌ Erreur critique : {str(e)}")
            break
