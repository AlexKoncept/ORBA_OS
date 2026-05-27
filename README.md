# 🔮 The Orba Ecosystem / L'Écosystème Orba

<p align="center">
  <img src="./orba_ecosystem.webp" alt="Orba OS Banner" width="650"/>
</p>

<p align="center">
  <a href="https://github.com/AlexKoncept/ORBA_OS/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License Apache 2.0"/></a>
  <img src="https://img.shields.io/badge/Kotlin-1.9-purple.svg" alt="Kotlin"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/Tauri-v2-FFC107.svg" alt="Tauri v2"/>
  <img src="https://img.shields.io/badge/LiteRT-Gemma--2B-orange.svg" alt="LiteRT Gemma 2B"/>
</p>

<p align="center">
  <b>A sovereign, cognitive, secure, and multimodal personal assistant suite.</b><br/>
  <i>Une suite logicielle d'assistants personnels souverains, cognitifs, sécurisés et multimodaux.</i>
</p>

<p align="center">
  <a href="#-english"><b>English Edition</b></a> • 
  <a href="#-français"><b>Édition Française</b></a>
</p>

---

## 🇺🇸 English

Welcome to the **Orba OS Ecosystem**—an intelligent personal assistant suite. This ecosystem is designed to run locally, offline, and transparently, unifying the smart agent experience across your mobile and desktop devices.

### Table of Contents
1. [Architecture](#architecture)
2. [Ecosystem Projects](#ecosystem-projects)
   - [Orba OS Mobile](#1-orba-os-mobile)
   - [Orba OS Desktop](#2-orba-os-desktop)
   - [Orba OS Website](#3-orba-os-website-landing-page)
3. [Sovereignty & Security Charter](#sovereignty--security-charter)
4. [Quick Start Guides](#quick-start-guides)
   - [Desktop Application Setup](#desktop-application-setup)
   - [Mobile Application Setup](#mobile-application-setup)
5. [License](#license)

---

### Architecture

```mermaid
graph TD
    A["ORBA ECOSYSTEM"] -->|Web| D["Website"]
    A -->|Desktop| C["Desktop"]
    A -->|Mobile| B["Mobile"]

### Ecosystem Projects

#### 1. 📱 [Orba OS Mobile](./Orba_OS_Mobile)
*   **Platform**: Android (Kotlin native, NDK C++).
*   **Objective**: A secure pocket assistant running fully offline on your smartphone's Neural Processing Unit (NPU).
*   **Key Components**:
    *   **Local STT & TTS**: Real-time native integration of Piper TTS via C++ JNI (`piper_jni.cpp`) injecting raw PCM audio directly to `AudioTrack`.
    *   **OrbaSphere UI**: Organic 3D orb rendering powered by AGSL Shaders, pulsating in real-time according to voice RMS decibels.
    *   **Offline Import**: File picker to import models (`gemma.bin` and Piper voice config) without requiring internet access.
    *   **System Tools**: Command router to trigger native actions offline (flashlight, silent mode, battery check).

#### 2. 🖥️ [Orba OS Desktop](./Orba_OS_Desktop)
*   **Platform**: Windows, macOS, Linux (Tauri v2 / FastAPI / Python).
*   **Objective**: A floating desktop assistant capable of executing local system operations safely.
*   **Key Components**:
    *   **OrbaSphere Desktop**: Borderless, transparent WebGL floating widget.
    *   **Guardrails (Human-in-the-Loop)** : Security popups to approve or reject critical tool calls (`write_file`, `delete_file`, `execute_command`).
    *   **Multi-Channel Gateways**: Control and remote validation via WhatsApp (Twilio) and Telegram.
    *   **Vision Agent & Scheduler**: Screen analysis via Gemini 1.5 & Pillow, background task scheduler (`scheduled_tasks.json`), and async Windows Toast Notifications.

#### 3. 🌐 [Orba OS Website](https://orba-website-byalexkoncept.netlify.app/)
*   **Platform**: Web (HTML5, Vanilla CSS, JS).
*   **Objective**: Showcase web platform presenting the project, roadmap phases, and download links with a premium Glassmorphism design.
*   **Link** : https://orbaproject-byalexkoncept.netlify.app/ 
---

### Sovereignty & Security Charter

1.  **Offline-First**: Local models (Ollama, LiteRT/Gemma) and local audio engines (Vosk, Piper) are always prioritized to ensure absolute data privacy.
2.  **Cognitive Transparency (ReAct Log)**: The agent displays its thought process (*thoughts*) and the tools it plans to call, avoiding black-box behavior.
3.  **User Control (Zero-Trust Guardrails)**: No critical system changes can run without human confirmation (local dialog box or remote SMS/WhatsApp keyword).

---

### Quick Start Guides

#### Desktop Application Setup

##### Step 1: Configure Python Backend
1. Navigate to the backend directory:
   ```bash
   cd Orba_OS_Desktop/backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows PowerShell: .venv\Scripts\Activate.ps1
   # Linux / macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in API keys if you wish to use Cloud models (Ollama local inference doesn't require any API key).
4. Start the server:
   ```bash
   python main.py
   ```
   The WebSocket and HTTP server will run on `http://127.0.0.1:8000`.

##### Step 2: Open User Console
*   Simply open the file **`Orba_OS_Desktop/frontend/index.html`** in your browser. The console connects automatically, turning the status light green.

##### Step 3: Run Tauri Desktop Widget
1. Install Tauri CLI at the root of `Orba_OS_Desktop`:
   ```bash
   npm install @tauri-apps/cli
   ```
2. Run the application in development mode (launches the floating transparent orb widget):
   ```bash
   npx tauri dev
   ```

#### Mobile Application Setup
1. Open the `Orba_OS_Mobile` folder in Android Studio.
2. Install **CMake** and **NDK (Side-by-side)** via SDK Manager.
3. Select the `demoDebug` build variant.
4. Compile and install the APK on a device running Android 13.0 (API 33+) with at least **6GB RAM**.
5. On the first launch, the `ModelDownloader` will download Gemma-2D-IT (~2.5GB) and the Piper voice model (~50MB) local files.

---

### License
This project is licensed under the **Apache License 2.0**. See the [LICENSE](./LICENSE) file for more information.

---
---

## 🇫🇷 Français

Bienvenue dans l'écosystème **Orba OS**—une suite d'assistants personnels intelligents conçus pour s'exécuter localement, hors-ligne et de manière transparente, unifiant l'expérience utilisateur sur vos appareils mobiles et de bureau.

### Table des Matières
1. [Architecture](#architecture-1)
2. [Les Projets de l'Écosystème](#les-projets-de-lécosystème)
   - [Orba OS Mobile](#1-orba-os-mobile-1)
   - [Orba OS Desktop](#2-orba-os-desktop-1)
   - [Orba OS Website](#3-orba-os-website-vitrine-web)
3. [Charte de Souveraineté & Sécurité](#charte-de-souveraineté--sécurité)
4. [Guides de Lancement Rapide](#guides-de-lancement-rapide)
   - [Configuration de la Version Bureau (Desktop)](#configuration-de-la-version-bureau-desktop)
   - [Configuration de la Version Mobile (Android)](#configuration-de-la-version-mobile-android)
5. [Licence](#licence)

---

### Architecture

```mermaid
graph TD
    A["ORBA ECOSYSTEM"] -->|Web| D["Website"]
    A -->|Desktop| C["Desktop"]
    A -->|Mobile| B["Mobile"]


### Les Projets de l'Écosystème

#### 1. 📱 [Orba OS Mobile](./Orba_OS_Mobile)
*   **Plateforme** : Android (Kotlin native, NDK C++).
*   **Objectif** : Un assistant de poche sécurisé, s'exécutant hors-ligne sur le coprocesseur neuronal (NPU) du smartphone.
*   **Composants clés** :
    *   **STT & TTS Locaux** : Intégration JNI C++ de Piper TTS (`piper_jni.cpp`) jouant des flux PCM directement sur un `AudioTrack` Android.
    *   **Interface OrbaSphere** : Orbite 3D animée via des Shaders AGSL s'exécutant sur le GPU, pulsant au rythme des décibels RMS du micro.
    *   **Import Hors-ligne** : Sélecteur de stockage local pour importer les modèles (`gemma.bin` et voix Piper) sans connexion internet.
    *   **Outils Système** : Routeur de commandes matérielles locales (lampe torche, mode silencieux, état batterie).

#### 2. 🖥️ [Orba OS Desktop](./Orba_OS_Desktop)
*   **Plateforme** : Windows, macOS, Linux (Tauri v2 / FastAPI / Python).
*   **Objectif** : Un assistant de bureau flottant, capable d'exécuter des outils d'administration locale en toute sécurité.
*   **Composants clés** :
    *   **OrbaSphere Desktop** : Widget flottant transparent WebGL sans bordures.
    *   **Guardrails (Human-in-the-Loop)** : Demandes d'approbation modales pour les appels système critiques (`write_file`, `delete_file`, commandes système).
    *   **Passerelles Multi-Canaux** : Pilotage et validation d'actions à distance via WhatsApp (Twilio) et Telegram.
    *   **Vision & Planification** : Analyse d'écran via Gemini 1.5 & Pillow, planification de tâches d'arrière-plan (`scheduled_tasks.json`) et notifications Toast Windows natives.

#### 3. 🌐 [Orba OS Website (Vitrine Web)](https://orba-website-byalexkoncept.netlify.app/)
*   **Plateforme** : Web (HTML5, Vanilla CSS, JS).
*   **Objectif** : Vitrine technologique interactive présentant le projet, sa feuille de route (Roadmap) et ses liens de téléchargement sous un style premium en Glassmorphism.
*   **Lien** : https://orbaproject-byalexkoncept.netlify.app/ 
---

### Charte de Souveraineté & Sécurité

1.  **Priorité Locale (Offline-First)** : Les modèles LLM locaux (Ollama, LiteRT/Gemma) et audio locaux (Vosk, Piper) sont privilégiés pour garantir la confidentialité absolue de vos données.
2.  **Transparence Sémantique (ReAct Log)** : L'agent affiche ouvertement ses "pensées" (*thoughts*) et les outils qu'il va exécuter, sans effet boîte noire.
3.  **Contrôle Utilisateur (Zero-Trust Guardrails)** : Aucune modification système critique n'est effectuée sans une approbation humaine explicite (pop-up ou confirmation SMS/WhatsApp).

---

### Guides de Lancement Rapide

#### Configuration de la Version Bureau (Desktop)

##### Étape 1 : Configurer le Backend FastAPI Python
1. Accédez au dossier backend :
   ```bash
   cd Orba_OS_Desktop/backend
   ```
2. Créez l'environnement virtuel et installez les dépendances :
   ```bash
   python -m venv .venv
   # Sous Windows PowerShell : .venv\Scripts\Activate.ps1
   # Sous Linux / macOS : source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copiez `.env.example` en `.env` et configurez vos clés API (Optionnel, Ollama local ne nécessite aucune clé).
4. Lancez le serveur :
   ```bash
   python main.py
   ```
   Le serveur WebSocket / HTTP démarrera sur `http://127.0.0.1:8000`.

##### Étape 2 : Lancer la Console Web
*   Double-cliquez simplement sur le fichier **`Orba_OS_Desktop/frontend/index.html`** pour l'ouvrir dans votre navigateur.

##### Étape 3 : Lancer le Widget Tauri Bureau
1. Installez le CLI Tauri à la racine de `Orba_OS_Desktop` :
   ```bash
   npm install @tauri-apps/cli
   ```
2. Démarrez l'application en mode développement :
   ```bash
   npx tauri dev
   ```

#### Configuration de la Version Mobile (Android)
1. Ouvrez le dossier `Orba_OS_Mobile` dans Android Studio.
2. Configurez **CMake** et le **NDK** via le SDK Manager.
3. Sélectionnez la variante de build `demoDebug`.
4. Compilez et déployez sur un appareil Android 13.0 (API 33+) doté de **6 Go de RAM** minimum.
5. Au premier boot, l'application effectue le téléchargement et la configuration locale de Gemma-2D-IT (~2.5 Go) et de la voix Piper (~50 Mo).

---

### Licence
Ce projet est distribué sous licence **Apache License 2.0**. Consultez le fichier [LICENSE](./LICENSE) pour plus d'informations.
