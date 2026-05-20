# Orba OS Desktop (Concept & Prototype)

Ce dossier contient le prototype d'**Orba OS Desktop**, une déclinaison pour ordinateurs (Windows, macOS, Linux) de l'assistant personnel cognitif Orba. Il implémente une interface web enrichie, la saisie hybride (clavier/voix), un visualiseur 3D interactif de l'OrbaSphere, et un système d'autorisation de sécurité (Guardrails / Human-in-the-loop).

---

## 🛠️ Structure du Projet

*   `backend/` : Serveur FastAPI Python gérant les communications WebSocket, le routage LLM (Ollama, Gemini, OpenAI, Claude), les outils d'administration système et le système d'approbation.
*   `frontend/` : Console utilisateur avec intégration WebGL/Canvas de l'OrbaSphere (réagissant aux états cognitifs et au volume sonore) et console de terminal émulée.

---

## 🚀 Lancement Rapide (Étape par Étape)

### Étape 1 : Configurer le Backend Python
1. Rendez-vous dans le dossier du backend :
   ```bash
   cd backend
   ```
2. Créez un environnement virtuel et installez les dépendances :
   ```bash
   python -m venv .venv
   # Activer l'environnement :
   # Sous Windows (PowerShell) : .venv\Scripts\Activate.ps1
   # Sous Linux / Mac : source .venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. Copiez le fichier `.env.example` vers `.env` et complétez vos clés API si vous souhaitez utiliser Gemini/ChatGPT/Claude (Ollama ne nécessite aucune clé).

4. Lancez le serveur backend :
   ```bash
   python main.py
   ```
   Le serveur WebSocket et HTTP sera actif sur `http://127.0.0.1:8000`.

### Étape 2 : Lancer le Frontend
1. Ouvrez simplement le fichier **`frontend/index.html`** dans votre navigateur internet (Chrome, Edge, Firefox ou Safari).
2. La console va se connecter automatiquement au serveur local. Le point lumineux dans le menu de gauche passera au **Vert ("En ligne")**.

---

## 🔒 Tester le système de Guardrails (Alerte de Sécurité)
Pour observer la sécurité "Human-in-the-loop" demandée :
1. Dans le champ de texte de la console, saisissez une phrase contenant le mot **"supprime"** ou **"delete"** (ex: *"Peux-tu supprimer ce fichier ?"*).
2. Observez l'OrbaSphere passer en **Cyan (état ANALYZING)**.
3. Une boîte de dialogue modale de sécurité va surgir au centre de l'écran, vous indiquant que l'agent tente d'exécuter l'action critique `delete_file` avec des paramètres système.
4. Si vous cliquez sur **Autoriser**, le backend reçoit le feu vert et simule l'action. Si vous cliquez sur **Refuser**, l'action est immédiatement bloquée.

---

## 💬 Configuration du Gateway WhatsApp (Twilio)

Orba OS Desktop peut être piloté directement par WhatsApp. Pour cela, nous utilisons l'API Twilio WhatsApp.

### ⚙️ Paramétrage du Webhook Twilio
1. Configurez vos clés Twilio dans le fichier `.env` (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`).
2. Exposez votre serveur local sur Internet à l'aide d'un outil comme **ngrok** :
   ```bash
   ngrok http 8000
   ```
3. Sur votre console développeur Twilio, configurez l'URL du webhook de réception (Incoming Messages) pour votre Sandbox WhatsApp avec l'adresse publique fournie par ngrok :
   ```text
   https://<votre-sous-domaine-ngrok>.ngrok-free.app/whatsapp/webhook
   ```

### 📱 Utilisation & Approbations à distance
* Envoyez un message WhatsApp comme *"Bonjour Orba"* à votre numéro sandbox Twilio pour lancer l'agent.
* Si vous demandez une action critique sur votre PC via WhatsApp (ex: *"Supprime mon fichier test.txt"*), Orba suspendra l'action et vous enverra un message d'alerte :
  > ⚠️ **Alerte de Sécurité Orba OS**
  > L'assistant souhaite exécuter une action critique sur votre PC...
  > Répondez par :
  > 👉 **OUI [ID-ACTION]** pour autoriser
  > 👉 **NON [ID-ACTION]** pour refuser
* Répondez par **OUI [ID]** depuis votre téléphone : l'action s'exécutera physiquement sur votre PC en tâche de fond et l'agent vous renverra le rapport de succès directement sur WhatsApp !

---

## 🖥️ Compilation & Lancement du Widget Bureau (Tauri v2)

Pour transformer l'application en un widget flottant interactif transparent (`OrbaSphere`) vivant sur votre bureau :

### Prérequis (Chaîne de compilation Rust)
1. Installez Rust en téléchargeant l'installateur officiel Windows depuis : https://rustup.rs/
2. Durant l'installation, assurez-vous que les outils de compilation C++ MSVC sont configurés (proposés automatiquement par Rustup si Visual Studio Build Tools n'est pas présent).

### Lancement en mode Développement
1. À la racine du dossier `Orba_OS_Desktop`, installez le CLI de Tauri :
   ```bash
   npm install @tauri-apps/cli
   ```
2. Lancez l'application en mode développement (cela compilera le binaire Rust et ouvrira le Widget OrbaSphere transparent sur votre bureau) :
   ```bash
   npx tauri dev
   ```

### Propriétés du Widget :
* **Border-less & Transparent** : Il n'a aucun cadre ni bordure système, et épouse parfaitement les contours sphériques et l'aura lumineuse d'Orba.
* **Always-on-top** : Il reste visible par-dessus vos autres fenêtres de travail pour être interpellé à tout moment.

---

## 🎙️ Utilisation de la Reconnaissance Vocale Locale (STT)

Orba OS Desktop intègre un moteur de Speech-to-Text (STT) hors-ligne basé sur **Vosk**.

### Activation :
1. Dans le fichier `.env` du backend, réglez la variable :
   ```env
   ENABLE_LOCAL_MIC=true
   ```
2. Au premier lancement, Vosk téléchargera automatiquement le modèle de langue française léger (~45 Mo) et l'initialisera.
3. Parlez naturellement dans votre micro. Le texte est décodé à la volée et transmis à l'agent local. L'état cognitif de l'orbe passera brièvement au **Violet ("Orba vous écoute...")** pendant l'interprétation.

---

## 🔊 Synthèse Vocale Locale (TTS) & Animation Rythmique

Orba OS Desktop intègre la synthèse vocale locale haute performance **Piper**.

### Configuration :
1. Téléchargez un modèle de voix française au format `.onnx` (par exemple `fr_FR-upmc-medium.onnx`) et son fichier `.json` associé depuis le catalogue officiel Piper.
2. Déposez-les dans un dossier `backend/models/`.
3. Configurez le chemin dans votre `.env` :
   ```env
   PIPER_MODEL_PATH=models/fr_FR-upmc-medium.onnx
   ```

### Fonctionnement & Visualisation :
* Lorsque l'agent formule une réponse, le serveur lit les tranches audio PCM générées par Piper en temps réel.
* Pour chaque bloc de son émis, le système calcule sa valeur **RMS (Root Mean Square)** qui représente l'intensité décibel de la voix à cet instant précis.
* Cette mesure de volume est poussée instantanément sur le canal WebSocket pour modifier la distorsion et les particules de l'**OrbaSphere (état SPEAKING - Jaune/Orange)**, la faisant pulser au rythme de la voix.
* *Note : Si la bibliothèque `piper` n'est pas installée, le système bascule automatiquement sur un mode simulation rythmique pour tester l'animation WebGL.*

---

## 🦙 Intégration d'Ollama (IA Locale et Souveraine)

Pour exécuter Orba OS Desktop de manière 100% autonome sur votre machine (sans clé API externe) :

### Configuration d'Ollama :
1. Téléchargez et installez Ollama depuis : https://ollama.com/
2. Téléchargez le modèle souhaité dans votre terminal (par exemple **Gemma** ou **Llama-3**) :
   ```bash
   ollama run gemma
   ```
3. Laissez Ollama tourner en arrière-plan sur son port par défaut (`http://localhost:11434`).
4. Dans le fichier `.env` de votre backend, assurez-vous que l'URL d'Ollama pointe vers votre instance :
   ```env
   OLLAMA_API_URL=http://localhost:11434/v1
   ```
5. Dans le menu de gauche de la console Web/Tauri, sélectionnez **"Ollama (Local)"** dans le menu déroulant des fournisseurs, indiquez le nom de votre modèle (ex: `gemma`) et commencez à chatter !
6. **Parsing Robuste** : Le backend extrait automatiquement le bloc de décision JSON, même si le modèle local génère des phrases conversationnelles introductives ou explicatives autour du JSON.

---

## 👁️ Agent Visuel, Planificateur & Notifications Proactives

Le prototype Orba OS Desktop intègre de nouvelles fonctionnalités d'agentivité autonome et d'interactions proactives :

### 1. Vision Agent (Analyse d'Écran)
* **Description** : L'outil `analyze_screen(query)` (catégorie `CRITICAL`) prend une capture d'écran de l'affichage actuel à l'aide de la bibliothèque Pillow et l'envoie en natif à l'API Gemini 1.5 avec le prompt d'analyse pour répondre aux questions visuelles de l'utilisateur (ex: *"Regarde mon écran et décris-moi le problème"*).
* **Sécurité** : Cette action déclenche systématiquement une demande d'autorisation de sécurité (Guardrails).
* **Dépendance** : `pip install pillow`.

### 2. Planificateur d'Arrière-plan (Local Scheduler)
* **Fonctionnement** : Un planificateur de tâches d'arrière-plan surveille en permanence (toutes les 15 secondes) un fichier local `scheduled_tasks.json` où sont stockées les routines de l'agent.
* **Outils de planification pour l'agent** :
  * `schedule_task(prompt, interval_minutes, time_daily)` : Permet à Orba de planifier ses propres tâches récurrentes ou différées (ex: toutes les 60 minutes, ou tous les jours à `08:00`).
  * `list_scheduled_tasks()` : Liste toutes les tâches enregistrées.
  * `unschedule_task(task_id)` : Supprime une tâche planifiée par son identifiant.

### 3. Notifications Push Windows Natives
* **Wake-up Proactif** : Lorsqu'une tâche programmée se déclenche, Orba OS utilise un appel PowerShell asynchrone pour générer une notification push Windows (Toast/Balloon Notification) sur le bureau utilisateur. Cela réveille le frontend et informe l'utilisateur de manière autonome de l'exécution en cours.
