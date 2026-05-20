import os
import json
import logging
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic

# Import our system tools
try:
    from tools import (
        TOOL_METADATA,
        list_directory,
        read_file,
        write_file,
        delete_file,
        open_app,
        execute_system_command,
        analyze_screen,
        schedule_task,
        list_scheduled_tasks,
        unschedule_task
    )
except ImportError:
    from .tools import (
        TOOL_METADATA,
        list_directory,
        read_file,
        write_file,
        delete_file,
        open_app,
        execute_system_command,
        analyze_screen,
        schedule_task,
        list_scheduled_tasks,
        unschedule_task
    )

try:
    from memory import OrbaMemoryManager
except ImportError:
    from .memory import OrbaMemoryManager

logger = logging.getLogger("OrbaDesktop.Agent")

class OrbaAgent:
    def __init__(self):
        # API Keys loaded from env vars
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.openai_key = os.environ.get("OPENAI_API_KEY", "")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        
        # Ollama local settings (defaulting to localhost:11434)
        self.ollama_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/v1")
        
        # Initialize clients
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        self.ollama_client = OpenAI(base_url=self.ollama_url, api_key="ollama")
        self.claude_client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
        # Initialize Long-term Encrypted Memory Manager
        self.memory_manager = OrbaMemoryManager()

        self.system_prompt = (
            "Tu es Orba OS, un assistant de bureau intelligent, souverain, proactif et chaleureux.\n"
            "Tu aides l'utilisateur à piloter son PC (Mac, Linux, Windows) par la voix ou par le clavier.\n\n"
            "Tu as accès aux outils locaux suivants :\n"
            "1. list_directory(path: str) -> Renvoie le contenu d'un dossier.\n"
            "2. read_file(filepath: str) -> Renvoie le contenu textuel d'un fichier.\n"
            "3. write_file(filepath: str, content: str) -> [CRITICAL] Écrit/écrase un fichier.\n"
            "4. delete_file(filepath: str) -> [CRITICAL] Supprime un fichier ou dossier.\n"
            "5. open_app(app_name: str) -> Lance une application locale (ex: 'notepad', 'calc').\n"
            "6. execute_system_command(command: str) -> [CRITICAL] Exécute une commande système.\n"
            "7. analyze_screen(query: str) -> [CRITICAL] Prend une capture d'écran de l'affichage actuel et l'analyse via Gemini pour répondre à la question (query).\n"
            "8. schedule_task(prompt: str, interval_minutes: int, time_daily: str) -> [CRITICAL] Planifie une action automatique à exécuter. Fournir soit 'interval_minutes' (ex: 60) soit 'time_daily' (format 'HH:MM', ex: '08:00') avec le 'prompt' à lancer.\n"
            "9. list_scheduled_tasks() -> Liste toutes les tâches planifiées d'arrière-plan.\n"
            "10. unschedule_task(task_id: str) -> [CRITICAL] Supprime une tâche planifiée par son ID.\n\n"
            "Pour communiquer avec l'orchestrateur, tu dois IMPÉRATIVEMENT répondre avec un format JSON strict, "
            "sans aucun formatage markdown (ne pas mettre de balises ```json ou de texte d'enrobage).\n"
            "Structure du JSON attendu :\n"
            "{\n"
            "  \"thought\": \"Ta réflexion interne étape par étape sur la requête de l'utilisateur.\",\n"
            "  \"tool\": \"nom_de_l_outil\" ou \"none\",\n"
            "  \"parameters\": {\"param_name\": \"value\"},\n"
            "  \"reply\": \"Le message final à afficher et à prononcer vocalement (laisser vide si tu appelles un outil).\"\n"
            "}\n\n"
            "Exemple 1 (Pas d'outil requis) :\n"
            "{\n"
            "  \"thought\": \"L'utilisateur me dit bonjour, je vais lui répondre amicalement.\",\n"
            "  \"tool\": \"none\",\n"
            "  \"parameters\": {},\n"
            "  \"reply\": \"Bonjour ! Comment puis-je vous aider sur votre ordinateur aujourd'hui ?\"\n"
            "}\n\n"
            "Exemple 2 (Appel d'outil) :\n"
            "{\n"
            "  \"thought\": \"L'utilisateur veut voir les fichiers de son répertoire actuel. J'appelle list_directory.\",\n"
            "  \"tool\": \"list_directory\",\n"
            "  \"parameters\": {\"path\": \".\"},\n"
            "  \"reply\": \"\"\n"
            "}\n"
        )

    def query_llm(self, prompt: str, provider: str, model: str) -> str:
        """Helper to fetch raw text response from provider, injecting RAG context if available."""
        # Retrieve relevant memories
        memories = self.memory_manager.search_memory(prompt, k=3)
        context_str = ""
        if memories:
            context_str = "\n\n[SOUVENIRS IMPORTANTS RETROUVÉS (MÉMOIRE LOCALE CHIFFRÉE)]\n"
            for m in memories:
                context_str += f"- {m}\n"
            context_str += "Utilise ces informations passées si elles sont pertinentes pour répondre à la requête actuelle."
            
        sys_prompt = self.system_prompt + context_str

        if provider == "gemini":
            if not self.gemini_key:
                raise ValueError("Clé API Gemini manquante dans le fichier .env.")
            gen_model = genai.GenerativeModel(
                model_name=model if model else "gemini-1.5-flash",
                system_instruction=sys_prompt
            )
            response = gen_model.generate_content(prompt)
            return response.text

        elif provider == "openai":
            if not self.openai_key:
                raise ValueError("Clé API OpenAI manquante dans le fichier .env.")
            response = self.openai_client.chat.completions.create(
                model=model if model else "gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        elif provider == "claude":
            if not self.anthropic_key:
                raise ValueError("Clé API Anthropic manquante dans le fichier .env.")
            response = self.claude_client.messages.create(
                model=model if model else "claude-3-haiku-20240307",
                max_tokens=1000,
                system=sys_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        elif provider == "ollama":
            response = self.ollama_client.chat.completions.create(
                model=model if model else "gemma",
                response_format={"type": "json_object"} if model != "gemma" else None,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        else:
            raise ValueError(f"Fournisseur '{provider}' inconnu.")

    def run_tool(self, tool_name: str, parameters: dict) -> str:
        """Execute a local system tool by name."""
        try:
            if tool_name == "list_directory":
                res = list_directory(parameters.get("path", "."))
                return f"Fichiers trouvés : {res}"
            elif tool_name == "read_file":
                res = read_file(parameters.get("filepath", ""))
                return f"Contenu du fichier : {res}"
            elif tool_name == "write_file":
                return write_file(parameters.get("filepath", ""), parameters.get("content", ""))
            elif tool_name == "delete_file":
                return delete_file(parameters.get("filepath", ""))
            elif tool_name == "open_app":
                return open_app(parameters.get("app_name", ""))
            elif tool_name == "execute_system_command":
                return execute_system_command(parameters.get("command", ""))
            elif tool_name == "analyze_screen":
                return analyze_screen(parameters.get("query", ""))
            elif tool_name == "schedule_task":
                return schedule_task(
                    parameters.get("prompt", ""),
                    int(parameters.get("interval_minutes", 0) or 0),
                    parameters.get("time_daily", "")
                )
            elif tool_name == "list_scheduled_tasks":
                return list_scheduled_tasks()
            elif tool_name == "unschedule_task":
                return unschedule_task(parameters.get("task_id", ""))
            else:
                return f"Erreur: Outil '{tool_name}' non reconnu."
        except Exception as e:
            return f"Exception lors de l'exécution de l'outil : {str(e)}"
