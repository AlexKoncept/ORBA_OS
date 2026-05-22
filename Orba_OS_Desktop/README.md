# Orba OS (Desktop Edition)
[🇺🇸 English](#english-version) | [🇫🇷 Français](#version-française)

---

<a id="english-version"></a>
## 🇺🇸 English Version

This folder contains the prototype of **Orba OS Desktop**, a version for computers (Windows, macOS, Linux) of the Orba cognitive personal assistant. It implements an enriched web interface, hybrid input (keyboard/voice), an interactive 3D visualizer of the OrbaSphere, and a security authorization system (Guardrails / Human-in-the-loop).

---

### 🛠️ Project Structure

*   `backend/`: Python FastAPI server managing WebSocket communications, LLM routing (Ollama, Gemini, OpenAI, Claude), system administration tools, and the approval system.
*   `frontend/`: User console with WebGL/Canvas integration of the OrbaSphere (reacting to cognitive states and sound volume) and an emulated terminal console.

---

### 🚀 Quick Start (Step by Step)

#### Step 1: Configure the Python Backend
1. Go to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Activate the environment:
   # On Windows (PowerShell): .venv\Scripts\Activate.ps1
   # On Linux / Mac: source .venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. Copy the `.env.example` file to `.env` and fill in your API keys if you want to use Gemini/ChatGPT/Claude (Ollama requires no key).

4. Start the backend server:
   ```bash
   python main.py
   ```
   The WebSocket and HTTP server will be active on `http://127.0.0.1:8000`.

#### Step 2: Launch the Frontend
1. Simply open the **`frontend/index.html`** file in your web browser (Chrome, Edge, Firefox, or Safari).
2. The console will automatically connect to the local server. The glowing dot in the left menu will turn **Green ("Online")**.

---

### 🔒 Testing the Guardrails System (Security Alert)
To observe the requested "Human-in-the-loop" security:
1. In the console's text field, enter a sentence containing the word **"supprime"** or **"delete"** (e.g., *"Can you delete this file?"*).
2. Observe the OrbaSphere turning **Cyan (ANALYZING state)**.
3. A security modal dialog will pop up in the center of the screen, indicating that the agent is trying to execute the critical action `delete_file` with system parameters.
4. If you click **Allow**, the backend gets the green light and simulates the action. If you click **Deny**, the action is immediately blocked.

---

### 💬 WhatsApp Gateway Configuration (Twilio)

Orba OS Desktop can be controlled directly via WhatsApp. For this, we use the Twilio WhatsApp API.

#### ⚙️ Twilio Webhook Setup
1. Configure your Twilio keys in the `.env` file (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`).
2. Expose your local server to the Internet using a tool like **ngrok**:
   ```bash
   ngrok http 8000
   ```
3. In your Twilio developer console, configure the incoming webhook URL (Incoming Messages) for your WhatsApp Sandbox with the public address provided by ngrok:
   ```text
   https://<your-ngrok-subdomain>.ngrok-free.app/whatsapp/webhook
   ```

#### 📱 Remote Usage & Approvals
* Send a WhatsApp message like *"Hello Orba"* to your Twilio sandbox number to start the agent.
* If you request a critical action on your PC via WhatsApp (e.g., *"Delete my test.txt file"*), Orba will pause the action and send you an alert message:
  > ⚠️ **Orba OS Security Alert**
  > The assistant wants to execute a critical action on your PC...
  > Reply with:
  > 👉 **YES [ACTION-ID]** to allow
  > 👉 **NO [ACTION-ID]** to deny
* Reply with **YES [ID]** from your phone: the action will physically execute on your PC in the background, and the agent will send you the success report directly on WhatsApp!

---

### 🖥️ Compilation & Launching the Desktop Widget (Tauri v2)

To transform the application into a transparent, interactive floating widget (`OrbaSphere`) living on your desktop:

#### Prerequisites (Rust Toolchain)
1. Install Rust by downloading the official Windows installer from: https://rustup.rs/
2. During installation, ensure the MSVC C++ build tools are configured (automatically offered by Rustup if Visual Studio Build Tools is not present).

#### Launching in Development Mode
1. At the root of the `Orba_OS_Desktop` folder, install the Tauri CLI:
   ```bash
   npm install @tauri-apps/cli
   ```
2. Launch the application in development mode (this will compile the Rust binary and open the transparent OrbaSphere Widget on your desktop):
   ```bash
   npx tauri dev
   ```

#### Widget Properties:
* **Border-less & Transparent**: It has no system frame or border, and perfectly hugs the spherical contours and glowing aura of Orba.
* **Always-on-top**: It remains visible over your other work windows so it can be called upon at any time.

---

### 🎙️ Using Local Speech Recognition (STT)

Orba OS Desktop integrates an offline Speech-to-Text (STT) engine based on **Vosk**.

#### Activation:
1. In the backend `.env` file, set the variable:
   ```env
   ENABLE_LOCAL_MIC=true
   ```
2. On first launch, Vosk will automatically download the lightweight language model (~45 MB) and initialize it.
3. Speak naturally into your microphone. The text is decoded on the fly and transmitted to the local agent. The orb's cognitive state will briefly turn **Purple ("Orba is listening...")** during interpretation.

---

### 🔊 Local Speech Synthesis (TTS) & Rhythmic Animation

Orba OS Desktop integrates the high-performance local speech synthesis **Piper**.

#### Configuration:
1. Download a voice model (e.g., `en_US-lessac-medium.onnx` or `fr_FR-upmc-medium.onnx`) in `.onnx` format and its associated `.json` file from the official Piper catalog.
2. Place them in a `backend/models/` folder.
3. Configure the path in your `.env`:
   ```env
   PIPER_MODEL_PATH=models/en_US-lessac-medium.onnx
   ```

#### Operation & Visualization:
* When the agent formulates a response, the server reads the PCM audio slices generated by Piper in real-time.
* For each block of sound emitted, the system calculates its **RMS (Root Mean Square)** value, which represents the decibel intensity of the voice at that exact moment.
* This volume measurement is pushed instantly over the WebSocket channel to modify the distortion and particles of the **OrbaSphere (SPEAKING state - Yellow/Orange)**, making it pulse to the rhythm of the voice.
* *Note: If the `piper` library is not installed, the system automatically falls back on a rhythmic simulation mode to test the WebGL animation.*

---

### 🦙 Integrating Ollama (Local and Sovereign AI)

To run Orba OS Desktop 100% autonomously on your machine (without an external API key):

#### Ollama Configuration:
1. Download and install Ollama from: https://ollama.com/
2. Download the desired model in your terminal (e.g., **Gemma** or **Llama-3**):
   ```bash
   ollama run gemma
   ```
3. Let Ollama run in the background on its default port (`http://localhost:11434`).
4. In your backend `.env` file, ensure the Ollama URL points to your instance:
   ```env
   OLLAMA_API_URL=http://localhost:11434/v1
   ```
5. In the left menu of the Web/Tauri console, select **"Ollama (Local)"** from the providers dropdown, enter your model name (e.g., `gemma`), and start chatting!
6. **Robust Parsing**: The backend automatically extracts the JSON decision block, even if the local model generates introductory or explanatory conversational sentences around the JSON.

---

### 👁️ Visual Agent, Scheduler & Proactive Notifications

The Orba OS Desktop prototype integrates new features for autonomous agency and proactive interactions:

#### 1. Vision Agent (Screen Analysis)
* **Description**: The `analyze_screen(query)` tool (`CRITICAL` category) takes a screenshot of the current display using the Pillow library and sends it natively to the Gemini 1.5 API along with the analysis prompt to answer the user's visual questions (e.g., *"Look at my screen and describe the problem to me"*).
* **Security**: This action systematically triggers a security authorization request (Guardrails).
* **Dependency**: `pip install pillow`.

#### 2. Background Scheduler (Local Scheduler)
* **Operation**: A background task scheduler continuously monitors (every 15 seconds) a local `scheduled_tasks.json` file where the agent's routines are stored.
* **Scheduling tools for the agent**:
  * `schedule_task(prompt, interval_minutes, time_daily)`: Allows Orba to schedule its own recurring or delayed tasks (e.g., every 60 minutes, or every day at `08:00`).
  * `list_scheduled_tasks()`: Lists all registered tasks.
  * `unschedule_task(task_id)`: Deletes a scheduled task by its identifier.

#### 3. Native Windows Push Notifications
* **Proactive Wake-up**: When a scheduled task is triggered, Orba OS uses an asynchronous PowerShell call to generate a Windows push notification (Toast/Balloon Notification) on the user's desktop. This wakes up the frontend and autonomously informs the user of the execution in progress.

---
---

<a id="version-française"></a>
## 🇫🇷 Version Française

Ce dossier contient le prototype d'**Orba OS Desktop**, une déclinaison pour ordinateurs (Windows, macOS, Linux) de l'assistant personnel cognitif Orba. Il implémente une interface web enrichie, la saisie hybride (clavier/voix), un visualiseur 3D interactif de l'OrbaSphere, et un système d'autorisation de sécurité (Guardrails / Human-in-the-loop).

---

### 🛠️ Structure du Projet

*   `backend/` : Serveur FastAPI Python gérant les communications WebSocket, le routage LLM (Ollama, Gemini, OpenAI, Claude), les outils d'administration système et le système d'approbation.
*   `frontend/` : Console utilisateur avec intégration WebGL/Canvas de l'OrbaSphere (réagissant aux états cognitifs et au volume sonore) et console de terminal émulée.

---

### 🚀 Lancement Rapide (Étape par Étape)

#### Étape 1 : Configurer le Backend Python
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

#### Étape 2 : Lancer le Frontend
1. Ouvrez simplement le fichier **`frontend/index.html`** dans votre navigateur internet (Chrome, Edge, Firefox ou Safari).
2. La console va se connecter automatiquement au serveur local. Le point lumineux dans le menu de gauche passera au **Vert ("En ligne")**.

---

### 🔒 Tester le système de Guardrails (Alerte de Sécurité)
Pour observer la sécurité "Human-in-the-loop" demandée :
1. Dans le champ de texte de la console, saisissez une phrase contenant le mot **"supprime"** ou **"delete"** (ex: *"Peux-tu supprimer ce fichier ?"*).
2. Observez l'OrbaSphere passer en **Cyan (état ANALYZING)**.
3. Une boîte de dialogue modale de sécurité va surgir au centre de l'écran, vous indiquant que l'agent tente d'exécuter l'action critique `delete_file` avec des paramètres système.
4. Si vous cliquez sur **Autoriser**, le backend reçoit le feu vert et simule l'action. Si vous cliquez sur **Refuser**, l'action est immédiatement bloquée.

---

### 💬 Configuration du Gateway WhatsApp (Twilio)

Orba OS Desktop peut être piloté directement par WhatsApp. Pour cela, nous utilisons l'API Twilio WhatsApp.

#### ⚙️ Paramétrage du Webhook Twilio
1. Configurez vos clés Twilio dans le fichier `.env` (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`).
2. Exposez votre serveur local sur Internet à l'aide d'un outil comme **ngrok** :
   ```bash
   ngrok http 8000
   ```
3. Sur votre console développeur Twilio, configurez l'URL du webhook de réception (Incoming Messages) pour votre Sandbox WhatsApp avec l'adresse publique fournie par ngrok :
   ```text
   https://<votre-sous-domaine-ngrok>.ngrok-free.app/whatsapp/webhook
   ```

#### 📱 Utilisation & Approbations à distance
* Envoyez un message WhatsApp comme *"Bonjour Orba"* à votre numéro sandbox Twilio pour lancer l'agent.
* Si vous demandez une action critique sur votre PC via WhatsApp (ex: *"Supprime mon fichier test.txt"*), Orba suspendra l'action et vous enverra un message d'alerte :
  > ⚠️ **Alerte de Sécurité Orba OS**
  > L'assistant souhaite exécuter une action critique sur votre PC...
  > Répondez par :
  > 👉 **OUI [ID-ACTION]** pour autoriser
  > 👉 **NON [ID-ACTION]** pour refuser
* Répondez par **OUI [ID]** depuis votre téléphone : l'action s'exécutera physiquement sur votre PC en tâche de fond et l'agent vous renverra le rapport de succès directement sur WhatsApp !

---

### 🖥️ Compilation & Lancement du Widget Bureau (Tauri v2)

Pour transformer l'application en un widget flottant interactif transparent (`OrbaSphere`) vivant sur votre bureau :

#### Prérequis (Chaîne de compilation Rust)
1. Installez Rust en téléchargeant l'installateur officiel Windows depuis : https://rustup.rs/
2. Durant l'installation, assurez-vous que les outils de compilation C++ MSVC sont configurés (proposés automatiquement par Rustup si Visual Studio Build Tools n'est pas présent).

#### Lancement en mode Développement
1. À la racine du dossier `Orba_OS_Desktop`, installez le CLI de Tauri :
   ```bash
   npm install @tauri-apps/cli
   ```
2. Lancez l'application en mode développement (cela compilera le binaire Rust et ouvrira le Widget OrbaSphere transparent sur votre bureau) :
   ```bash
   npx tauri dev
   ```

#### Propriétés du Widget :
* **Border-less & Transparent** : Il n'a aucun cadre ni bordure système, et épouse parfaitement les contours sphériques et l'aura lumineuse d'Orba.
* **Always-on-top** : Il reste visible par-dessus vos autres fenêtres de travail pour être interpellé à tout moment.

---

### 🎙️ Utilisation de la Reconnaissance Vocale Locale (STT)

Orba OS Desktop intègre un moteur de Speech-to-Text (STT) hors-ligne basé sur **Vosk**.

#### Activation :
1. Dans le fichier `.env` du backend, réglez la variable :
   ```env
   ENABLE_LOCAL_MIC=true
   ```
2. Au premier lancement, Vosk téléchargera automatiquement le modèle de langue française léger (~45 Mo) et l'initialisera.
3. Parlez naturellement dans votre micro. Le texte est décodé à la volée et transmis à l'agent local. L'état cognitif de l'orbe passera brièvement au **Violet ("Orba vous écoute...")** pendant l'interprétation.

---

### 🔊 Synthèse Vocale Locale (TTS) & Animation Rythmique

Orba OS Desktop intègre la synthèse vocale locale haute performance **Piper**.

#### Configuration :
1. Téléchargez un modèle de voix française au format `.onnx` (par exemple `fr_FR-upmc-medium.onnx`) et son fichier `.json` associé depuis le catalogue officiel Piper.
2. Déposez-les dans un dossier `backend/models/`.
3. Configurez le chemin dans votre `.env` :
   ```env
   PIPER_MODEL_PATH=models/fr_FR-upmc-medium.onnx
   ```

#### Fonctionnement & Visualisation :
* Lorsque l'agent formule une réponse, le serveur lit les tranches audio PCM générées par Piper en temps réel.
* Pour chaque bloc de son émis, le système calcule sa valeur **RMS (Root Mean Square)** qui représente l'intensité décibel de la voix à cet instant précis.
* Cette mesure de volume est poussée instantanément sur le canal WebSocket pour modifier la distorsion et les particules de l'**OrbaSphere (état SPEAKING - Jaune/Orange)**, la faisant pulser au rythme de la voix.
* *Note : Si la bibliothèque `piper` n'est pas installée, le système bascule automatiquement sur un mode simulation rythmique pour tester l'animation WebGL.*

---

### 🦙 Intégration d'Ollama (IA Locale et Souveraine)

Pour exécuter Orba OS Desktop de manière 100% autonome sur votre machine (sans clé API externe) :

#### Configuration d'Ollama :
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

### 👁️ Agent Visuel, Planificateur & Notifications Proactives

Le prototype Orba OS Desktop intègre de nouvelles fonctionnalités d'agentivité autonome et d'interactions proactives :

#### 1. Vision Agent (Analyse d'Écran)
* **Description** : L'outil `analyze_screen(query)` (catégorie `CRITICAL`) prend une capture d'écran de l'affichage actuel à l'aide de la bibliothèque Pillow et l'envoie en natif à l'API Gemini 1.5 avec le prompt d'analyse pour répondre aux questions visuelles de l'utilisateur (ex: *"Regarde mon écran et décris-moi le problème"*).
* **Sécurité** : Cette action déclenche systématiquement une demande d'autorisation de sécurité (Guardrails).
* **Dépendance** : `pip install pillow`.

#### 2. Planificateur d'Arrière-plan (Local Scheduler)
* **Fonctionnement** : Un planificateur de tâches d'arrière-plan surveille en permanence (toutes les 15 secondes) un fichier local `scheduled_tasks.json` où sont stockées les routines de l'agent.
* **Outils de planification pour l'agent** :
  * `schedule_task(prompt, interval_minutes, time_daily)` : Permet à Orba de planifier ses propres tâches récurrentes ou différées (ex: toutes les 60 minutes, ou tous les jours à `08:00`).
  * `list_scheduled_tasks()` : Liste toutes les tâches enregistrées.
  * `unschedule_task(task_id)` : Supprime une tâche planifiée par son identifiant.

#### 3. Notifications Push Windows Natives
* **Wake-up Proactif** : Lorsqu'une tâche programmée se déclenche, Orba OS utilise un appel PowerShell asynchrone pour générer une notification push Windows (Toast/Balloon Notification) sur le bureau utilisateur. Cela réveille le frontend et informe l'utilisateur de manière autonome de l'exécution en cours.
