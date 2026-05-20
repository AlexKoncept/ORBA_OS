import os
import shutil
import platform
import subprocess
import logging

logger = logging.getLogger("OrbaDesktop.Tools")

# Tool safety category mapping
TOOL_METADATA = {
    "list_directory": {"category": "SAFE", "desc": "Lister le contenu d'un dossier."},
    "read_file": {"category": "SAFE", "desc": "Lire le contenu d'un fichier texte."},
    "write_file": {"category": "CRITICAL", "desc": "Créer ou écraser un fichier sur le disque."},
    "delete_file": {"category": "CRITICAL", "desc": "Supprimer définitivement un fichier."},
    "open_app": {"category": "SAFE", "desc": "Lancer une application locale (ex: Bloc-notes, Navigateur)."},
    "system_command": {"category": "CRITICAL", "desc": "Exécuter une commande système dans le terminal."},
    "analyze_screen": {"category": "CRITICAL", "desc": "Prendre une capture d'écran du bureau et l'analyser pour répondre à une question."},
    "schedule_task": {"category": "CRITICAL", "desc": "Planifier une action automatique récurrente ou différée."},
    "list_scheduled_tasks": {"category": "SAFE", "desc": "Lister toutes les tâches d'arrière-plan planifiées."},
    "unschedule_task": {"category": "CRITICAL", "desc": "Supprimer une tâche d'arrière-plan planifiée."}
}

def list_directory(path: str = ".") -> list:
    """List directory contents safely."""
    try:
        resolved_path = os.path.abspath(path)
        return os.listdir(resolved_path)
    except Exception as e:
        return [f"Erreur lors de la lecture du dossier : {str(e)}"]

def read_file(filepath: str) -> str:
    """Read local file content safely."""
    try:
        resolved_path = os.path.abspath(filepath)
        if not os.path.exists(resolved_path):
            return "Erreur: Fichier introuvable."
        
        # Read first 5000 characters for safety
        with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(5000)
    except Exception as e:
        return f"Erreur lors du décodage du fichier : {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Write content to a file (CRITICAL tool)."""
    try:
        resolved_path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Fichier écrit avec succès dans {resolved_path}."
    except Exception as e:
        return f"Erreur d'écriture : {str(e)}"

def delete_file(filepath: str) -> str:
    """Delete a local file (CRITICAL tool)."""
    try:
        resolved_path = os.path.abspath(filepath)
        if not os.path.exists(resolved_path):
            return "Erreur: Le fichier à supprimer n'existe pas."
        
        if os.path.isdir(resolved_path):
            shutil.rmtree(resolved_path)
            return f"Dossier {resolved_path} supprimé avec succès."
        else:
            os.remove(resolved_path)
            return f"Fichier {resolved_path} supprimé avec succès."
    except Exception as e:
        return f"Erreur lors de la suppression : {str(e)}"

def open_app(app_name: str) -> str:
    """Launch local system applications depending on OS."""
    try:
        sys_type = platform.system()
        if sys_type == "Windows":
            if "notepad" in app_name.lower():
                subprocess.Popen(["notepad.exe"])
            elif "calc" in app_name.lower():
                subprocess.Popen(["calc.exe"])
            else:
                os.system(f"start {app_name}")
        elif sys_type == "Darwin": # macOS
            subprocess.Popen(["open", "-a", app_name])
        else: # Linux
            subprocess.Popen([app_name])
        return f"Application {app_name} démarrée."
    except Exception as e:
        return f"Impossible de lancer {app_name} : {str(e)}"

def execute_system_command(command: str) -> str:
    """Run shell commands (CRITICAL tool)."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=10.0)
        output = result.stdout + "\n" + result.stderr
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Erreur : Temps d'exécution dépassé (Timeout)."
    except Exception as e:
        return f"Erreur système : {str(e)}"

def analyze_screen(query: str) -> str:
    """Prend une capture d'écran du bureau et l'analyse via l'API Gemini pour répondre à la question."""
    try:
        from PIL import ImageGrab
    except ImportError:
        return "Erreur : La bibliothèque 'pillow' n'est pas installée. Veuillez lancer 'pip install pillow' pour utiliser cette fonctionnalité."

    try:
        import google.generativeai as genai
        
        # Capture screen
        img = ImageGrab.grab()
        
        # Check API key
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return "Erreur : Clé API Gemini manquante dans le fichier .env. Impossible d'analyser la capture d'écran."
            
        genai.configure(api_key=api_key)
        
        # Query Gemini 1.5 with the image object directly
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([query, img])
        return response.text
    except Exception as e:
        return f"Erreur lors de l'analyse d'écran : {str(e)}"

def schedule_task(prompt: str, interval_minutes: int = 0, time_daily: str = "") -> str:
    """Planifie une tâche récurrente ou quotidienne."""
    import json
    import uuid
    from datetime import datetime, timedelta
    
    tasks_file = os.path.abspath("scheduled_tasks.json")
    tasks = []
    if os.path.exists(tasks_file):
        try:
            with open(tasks_file, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        except Exception:
            tasks = []
            
    now = datetime.now()
    next_run = now
    
    if interval_minutes > 0:
        next_run = now + timedelta(minutes=interval_minutes)
    elif time_daily:
        try:
            parts = time_daily.split(":")
            hh = int(parts[0])
            mm = int(parts[1])
            scheduled_time = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)
            next_run = scheduled_time
        except Exception:
            return f"Format de l'heure invalide ({time_daily}). Utilisez le format HH:MM."
    else:
        return "Erreur : Spécifiez soit 'interval_minutes' soit 'time_daily'."
        
    task_id = str(uuid.uuid4())[:8]
    new_task = {
        "id": task_id,
        "prompt": prompt,
        "interval_minutes": interval_minutes,
        "time_daily": time_daily,
        "next_run": next_run.isoformat(),
        "enabled": True
    }
    
    tasks.append(new_task)
    try:
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return f"Erreur d'écriture du fichier de planification : {str(e)}"
        
    sched_desc = f"toutes les {interval_minutes} minutes" if interval_minutes > 0 else f"tous les jours à {time_daily}"
    return f"Tâche '{prompt}' planifiée avec succès (ID: {task_id}, prévue {sched_desc}, prochain lancement: {next_run.strftime('%Y-%m-%d %H:%M:%S')})."

def list_scheduled_tasks() -> str:
    """Lister toutes les tâches d'arrière-plan planifiées."""
    import json
    tasks_file = os.path.abspath("scheduled_tasks.json")
    if not os.path.exists(tasks_file):
        return "Aucune tâche planifiée."
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        if not tasks:
            return "Aucune tâche planifiée."
        res = "Liste des tâches planifiées :\n"
        for t in tasks:
            sched = f"toutes les {t['interval_minutes']} min" if t['interval_minutes'] > 0 else f"tous les jours à {t['time_daily']}"
            status = "Actif" if t.get("enabled", True) else "Désactivé"
            res += f"- [{status}] ID: {t['id']} | Prompt: '{t['prompt']}' | Récurrence: {sched} | Suivant: {t['next_run']}\n"
        return res
    except Exception as e:
        return f"Erreur de lecture des tâches : {str(e)}"

def unschedule_task(task_id: str) -> str:
    """Supprimer une tâche d'arrière-plan planifiée."""
    import json
    tasks_file = os.path.abspath("scheduled_tasks.json")
    if not os.path.exists(tasks_file):
        return "Aucune tâche planifiée trouvée."
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        
        updated_tasks = [t for t in tasks if t['id'] != task_id]
        if len(updated_tasks) == len(tasks):
            return f"Aucune tâche trouvée avec l'ID {task_id}."
            
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(updated_tasks, f, indent=4, ensure_ascii=False)
        return f"Tâche planifiée {task_id} supprimée avec succès."
    except Exception as e:
        return f"Erreur lors de la suppression : {str(e)}"
