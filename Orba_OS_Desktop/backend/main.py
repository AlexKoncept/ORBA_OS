import os
import asyncio
import json
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our Agent and Tool metadata
from agent import OrbaAgent
from tools import TOOL_METADATA
from whatsapp_gateway import whatsapp_router
from stt import LocalSTT
from tts import LocalTTS

# Initialize dotenv
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OrbaDesktop")

app = FastAPI(title="Orba OS Desktop Backend", version="3.0")
app.include_router(whatsapp_router)

# Initialize STT Listener
stt_listener = LocalSTT(lang="fr")
# Initialize TTS Engine
tts = LocalTTS()

@app.on_event("startup")
async def startup_event():
    # Load TTS voices
    tts.initialize()
    
    # Only boot mic if configured in .env
    enable_mic = os.environ.get("ENABLE_LOCAL_MIC", "false").lower() == "true"
    if enable_mic:
        logger.info("Démarrage de l'écoute microphone locale...")
        asyncio.create_task(run_stt_listener())
    else:
        logger.info("Écoute microphone locale désactivée (Activez ENABLE_LOCAL_MIC=true dans .env pour l'activer).")
        
    # Start scheduled tasks loop
    logger.info("Démarrage du planificateur de tâches d'arrière-plan...")
    asyncio.create_task(run_scheduled_tasks_loop())


async def run_stt_listener():
    async def stt_callback(text: str):
        global current_orba_state
        if current_orba_state in ("SPEAKING", "THINKING", "ANALYZING"):
            logger.info(f"STT ignoré en raison de l'état {current_orba_state} : {text}")
            return
        # Notify state changes and queue agent loop
        await notify_state("LISTENING", f"Message vocaux détectés : {text}")
        asyncio.create_task(run_agent_loop(text, provider="ollama", model="gemma"))
    
    try:
        await stt_listener.listen_loop(stt_callback)
    except Exception as e:
        logger.error(f"Erreur dans le thread micro STT : {e}")



# Allow CORS for local frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"UI Connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"UI Disconnected. Active connections: {len(self.active_connections)}")

    async def send_json(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send websocket message: {e}")

manager = ConnectionManager()

# Global state for pending approvals
pending_approvals = {}
current_orba_state = "IDLE"

class ChatRequest(BaseModel):
    message: str
    provider: str = "openai" # "openai" (for Ollama), "gemini", "claude"
    model: str = "gemma"

class ApprovalResponse(BaseModel):
    action_id: str
    approved: bool

# Instantiate the agent
agent = OrbaAgent()

@app.get("/status")
def read_status():
    return {"status": "running", "orba_state": "IDLE"}

@app.post("/approve")
async def approve_action(response: ApprovalResponse):
    action_id = response.action_id
    if action_id in pending_approvals:
        future = pending_approvals[action_id]
        if not future.done():
            future.set_result(response.approved)
        return {"status": "success", "message": f"Action {action_id} resolved with approved={response.approved}"}
    return {"status": "error", "message": f"Action ID {action_id} not found or expired"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send system startup diagnostics to the newly connected UI
    enable_mic = os.environ.get("ENABLE_LOCAL_MIC", "false").lower() == "true"
    if enable_mic:
        stt_status = "Actif (Vosk)" if stt_listener.model else "Inactif (Erreur d'initialisation)"
    else:
        stt_status = "Désactivé (Activez ENABLE_LOCAL_MIC=true dans .env)"
    
    tts_status = "Actif (Piper ONNX)" if tts.voice else "Simulation (piper-tts non installé ou modèle vocal absent)"
    
    await notify_terminal("DIAGNOSTIC", f"Reconnaissance Vocale (STT) : {stt_status}", "success" if "Actif" in stt_status else "system")
    await notify_terminal("DIAGNOSTIC", f"Synthèse Vocale (TTS) : {tts_status}", "success" if "Actif" in tts_status else "state-cyan")

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            logger.info(f"Received WebSocket event: {event}")
            
            # Handle events from the UI
            event_type = event.get("type")
            if event_type == "chat_message":
                text = event.get("text")
                provider = event.get("provider", "gemini")
                model = event.get("model", "gemini-1.5-flash")
                
                # Run the agent task asynchronously
                asyncio.create_task(run_agent_loop(text, provider, model))
                
            elif event_type == "approval_response":
                action_id = event.get("action_id")
                approved = event.get("approved")
                if action_id in pending_approvals:
                    future = pending_approvals[action_id]
                    if not future.done():
                        future.set_result(approved)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def notify_state(state: str, details: str = ""):
    """Send state updates (IDLE, LISTENING, THINKING, SPEAKING, ANALYZING) to the UI."""
    global current_orba_state
    current_orba_state = state
    await manager.send_json({
        "type": "state_change",
        "state": state,
        "details": details
    })

async def notify_volume(volume: float):
    """Send voice volume metrics to animate the OrbaSphere."""
    await manager.send_json({
        "type": "volume_update",
        "volume": volume
    })

async def notify_terminal(badge: str, text: str, style: str = "system"):
    """Update UI terminal emulation console."""
    await manager.send_json({
        "type": "terminal_log",
        "badge": badge,
        "text": text,
        "style": style
    })

async def request_human_approval(action_id: str, tool_name: str, parameters: dict) -> bool:
    """Prompt the user for permission to execute a critical command."""
    logger.info(f"Requesting approval for {tool_name} with params: {parameters}")
    
    # Send event to Frontend (Tauri/WebUI)
    await manager.send_json({
        "type": "approval_required",
        "action_id": action_id,
        "tool": tool_name,
        "parameters": parameters
    })
    
    # Notify messageries or local console
    await notify_terminal("GUARDRAIL", f"Approbation requise pour exécuter {tool_name}({parameters})", "state-cyan")
    
    # Create future to wait for response (WebSocket or HTTP post)
    future = asyncio.get_running_loop().create_future()
    pending_approvals[action_id] = future
    
    timeout_val = float(os.environ.get("ORBA_APPROVAL_TIMEOUT", "60.0"))
    try:
        # Wait for approval
        approved = await asyncio.wait_for(future, timeout=timeout_val)
        return approved
    except asyncio.TimeoutError:
        logger.warning(f"Approval timeout for action {action_id}")
        return False
    finally:
        if action_id in pending_approvals:
            del pending_approvals[action_id]

def show_system_notification(title: str, message: str):
    """Affiche une notification push Toast/Balloon native sous Windows via PowerShell."""
    import subprocess
    import platform
    
    if platform.system() != "Windows":
        logger.info(f"Notification (Non-Windows) -> {title} : {message}")
        return
        
    escaped_title = title.replace("'", "''")
    escaped_message = message.replace("'", "''")
    
    ps_cmd = (
        "[Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')|Out-Null;"
        "$bal=New-Object Windows.Forms.NotifyIcon;"
        "$bal.Icon=[Drawing.SystemIcons]::Information;"
        f"$bal.BalloonTipTitle='{escaped_title}';"
        f"$bal.BalloonTipText='{escaped_message}';"
        "$bal.Visible=$true;"
        "$bal.ShowBalloonTip(5000);"
        "Start-Sleep -s 1;"
        "$bal.Dispose();"
    )
    
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        logger.error(f"Impossible d'afficher la notification système : {e}")

async def run_scheduled_tasks_loop():
    """Boucle de planification en arrière-plan d'Orba OS."""
    tasks_file = os.path.abspath("scheduled_tasks.json")
    logger.info(f"Démarrage du boucle du planificateur local. Fichier: {tasks_file}")
    
    while True:
        await asyncio.sleep(15) # Vérification toutes les 15 secondes
        if not os.path.exists(tasks_file):
            continue
            
        try:
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except Exception:
            continue
            
        now = datetime.now()
        updated = False
        
        for t in tasks:
            if not t.get("enabled", True):
                continue
                
            next_run_str = t.get("next_run")
            if not next_run_str:
                continue
                
            try:
                next_run = datetime.fromisoformat(next_run_str)
            except Exception:
                continue
                
            if now >= next_run:
                prompt = t["prompt"]
                logger.info(f"Déclenchement automatique de la tâche planifiée : {prompt}")
                
                # Notification sur la console WebUI si elle est connectée
                try:
                    await notify_terminal("PLANIFICATEUR", f"Exécution automatique : '{prompt}'", "state-cyan")
                except Exception:
                    pass
                    
                # Notification push OS
                show_system_notification("Orba OS — Planificateur", f"Lancement de la tâche : '{prompt}'")
                
                # Exécution asynchrone de la boucle d'agent
                provider = os.environ.get("ORBA_DEFAULT_PROVIDER", "gemini")
                model = os.environ.get("ORBA_DEFAULT_MODEL", "gemini-1.5-flash")
                asyncio.create_task(run_agent_loop(prompt, provider, model))
                
                # Recalculer le prochain lancement
                if t.get("interval_minutes", 0) > 0:
                    t["next_run"] = (now + timedelta(minutes=t["interval_minutes"])).isoformat()
                elif t.get("time_daily", ""):
                    try:
                        parts = t["time_daily"].split(":")
                        hh = int(parts[0])
                        mm = int(parts[1])
                        scheduled_time = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
                        scheduled_time += timedelta(days=1)
                        t["next_run"] = scheduled_time.isoformat()
                    except Exception:
                        t["enabled"] = False
                else:
                    t["enabled"] = False
                    
                updated = True
                
        if updated:
            try:
                with open(tasks_file, "w", encoding="utf-8") as f:
                    json.dump(tasks, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement des tâches planifiées : {e}")

async def speak_text(text: str):
    """Play speech local TTS and notify state/terminal."""
    await notify_state("SPEAKING", "Synthèse vocale...")
    await notify_terminal("SPEAKING", text, "speaking")
    
    # Callback to push RMS volume metric to the WebUI
    def rms_callback(rms: float):
        asyncio.create_task(notify_volume(rms))
        
    await tts.speak(text, rms_callback)

async def run_agent_loop(user_text: str, provider: str, model: str):
    logger.info(f"Agent Loop started for query: {user_text}")
    await notify_terminal("USER", user_text, "user")
    
    # Retrieve relevant memories for user feedback
    memories = agent.memory_manager.search_memory(user_text, k=3)
    if memories:
        await notify_terminal("MEMOIRE", f"{len(memories)} souvenirs locaux pertinents récupérés et déchiffrés.", "state-cyan")
        
    # We can loop up to 3 turns to allow the agent to chain thoughts/tools
    max_turns = 3
    current_prompt = user_text
    
    for turn in range(max_turns):
        await notify_state("THINKING", "Inférence du modèle...")
        await notify_terminal("THINKING", f"Inférence via {provider}:{model} (Tour {turn+1})...", "thinking")
        
        try:
            # Query LLM (which returns JSON as string)
            raw_response = await asyncio.to_thread(agent.query_llm, current_prompt, provider, model)
            logger.info(f"LLM Raw response: {raw_response}")
            
            # Parse JSON response (robust against conversational prefix/suffix from local Ollama models)
            start_idx = raw_response.find('{')
            end_idx = raw_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_part = raw_response[start_idx:end_idx + 1]
                response_json = json.loads(json_part)
            else:
                raise ValueError("Format JSON invalide dans la réponse du modèle")
                
            thought = response_json.get("thought", "")
            tool_name = response_json.get("tool", "none")
            parameters = response_json.get("parameters", {})
            reply = response_json.get("reply", "")
            
            if thought:
                await notify_terminal("THINKING", f"Pensée : {thought}", "thinking")
                
            if tool_name == "none" or not tool_name:
                # Final response
                if reply:
                    await speak_text(reply)
                    agent.memory_manager.add_memory(f"Utilisateur : {user_text}\nOrba : {reply}")
                break
                
            # Execute tool
            if tool_name in TOOL_METADATA:
                meta = TOOL_METADATA[tool_name]
                category = meta.get("category", "SAFE")
                desc = meta.get("desc", "")
                
                await notify_terminal("SYSTEM", f"Appel d'outil : {tool_name} ({desc})", "system")
                
                approved = True
                if category == "CRITICAL":
                    await notify_state("ANALYZING", "Validation de sécurité requise...")
                    import uuid
                    action_id = str(uuid.uuid4())
                    approved = await request_human_approval(action_id, tool_name, parameters)
                    
                if approved:
                    await notify_terminal("GUARDRAIL", "Action autorisée.", "success")
                    await notify_state("ANALYZING", "Exécution de l'outil...")
                    
                    # Run the tool blocking-call in a thread pool to avoid blocking the event loop
                    tool_output = await asyncio.to_thread(agent.run_tool, tool_name, parameters)
                    await notify_terminal("SYSTEM", f"Résultat : {tool_output}", "system")
                    
                    # Feed the output back to the LLM for the next turn
                    current_prompt = f"Résultat de l'outil {tool_name} : {tool_output}\n\nRéponds maintenant à l'utilisateur ou enchaîne avec un autre outil si nécessaire."
                else:
                    await notify_terminal("GUARDRAIL", "Action refusée par l'utilisateur. Annulation.", "system")
                    await speak_text("Action annulée. Je ne peux pas modifier ou supprimer ce fichier sans votre accord.")
                    break
            else:
                await notify_terminal("SYSTEM", f"Erreur : Outil '{tool_name}' inconnu.", "system")
                break
                
        except json.JSONDecodeError:
            # If the model didn't return JSON, display it as raw text
            logger.warning("Failed to parse JSON from LLM response.")
            await speak_text(raw_response)
            break
        except Exception as e:
            logger.error(f"Error in agent execution loop: {e}")
            await notify_terminal("SYSTEM", f"Erreur critique : {str(e)}", "system")
            break
            
    await notify_state("IDLE", "Orba est en veille")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
