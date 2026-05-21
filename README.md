# 🔮 The Orba Ecosystem

<p align="center">
  <img src="orba_ecosystem.webp" alt="Orba OS Logo" width="220" style="border-radius: 50%;"/>
</p>

<p align="center">
  <a href="https://orba-ecosystem-project-byalexkoncept.netlify.app/"><img src="https://img.shields.io/badge/Website-Live-f03ea5?style=for-the-badge&logo=netlify" alt="Website"></a>
  <img src="https://img.shields.io/badge/Platform-Android%20%7C%20Windows%20%7C%20macOS%20%7C%20Linux-410056?style=for-the-badge" alt="Platforms">
  <img src="https://img.shields.io/badge/Architecture-Offline--First%20%7C%20Agentic-black?style=for-the-badge" alt="Architecture">
</p>

<p align="center">
  <a href="#-version-française"><b>Version Française 🇫🇷</b></a> • 
  <a href="#-english-version"><b>English Version 🇬🇧</b></a>
</p>

---

## 🇫🇷 Version Française

Bienvenue dans l'écosystème d'**Orba OS**, une suite logicielle d'assistants personnels souverains, cognitifs, sécurisés et multimodaux. Cet écosystème unifie l'expérience de l'agent personnel intelligent sur l'ensemble de vos appareils, du mobile à l'ordinateur de bureau.

### 🗺️ Architecture de l'Écosystème

L'écosystème orchestre trois briques complémentaires et interconnectées :

```mermaid
graph TD
    A["ORBA ECOSYSTEM (Souverain & Agentique)"] --> B["Orba OS Mobile (Android App)"]
    A --> C["Orba OS Desktop (Tauri / FastAPI)"]
    A --> D["Orba OS Website (Landing Page Showcase)"]

    B --> B1["Modèle Local JNI C++ / Kotlin"]
    B --> B2["Synthèse Vocale locale (Piper JNI)"]
    B --> B3["OrbaSphere Mobile UI"]

    C --> C1["Boucle Cognitive ReAct Python"]
    C --> C2["Visualiseur WebGL / Canvas"]
    C --> C3["Gateways (Micro local, Telegram, WhatsApp)"]

    D --> D1["Roadmap Interactive"]
    D --> D2["Aesthetics V3 Glassmorphism"]

🛠️ Les Composants du Projet

📱 1. Orba OS Mobile
Plateforme : Android (Kotlin native, NDK C++).

Objectif : Un assistant de poche sécurisé, capable de s'exécuter hors-ligne sur le processeur neuronal (NPU) du smartphone.

Composants clés :

Reconnaissance et synthèse vocale locale via l'intégration JNI de Piper TTS.

Synchronisation asynchrone des flux audios et protection de la RAM.

Import Local Manuel : Sélecteur système pour importer manuellement les modèles (gemma.bin et voix Piper) hors-ligne.

Classifieur vocal normalisé : Tokenisation et classification d'intentions vocales insensible aux accents (normalisation Unicode).

🖥️ 2. Orba OS Desktop
Plateforme : Windows, macOS, Linux (Tauri v2 / FastAPI / Python).

Objectif : Un assistant de bureau flottant et autonome, capable d'exécuter des outils système sur votre ordinateur en toute sécurité.

Composants clés :

OrbaSphere : Widget circulaire WebGL transparent, sans bordures, flottant au-dessus du bureau.

Système Guardrails (Human-in-the-loop) : Interception automatique des commandes système critiques avec demandes d'autorisation.

Passerelles Multi-Canaux : Pilotage et validation à distance via Telegram ou WhatsApp (Twilio).

STT & TTS locaux : Moteurs hors-ligne Vosk (reconnaissance) et Piper (parole) avec synchronisation visuelle (RMS).

Planificateur & Notifications : Boucle de tâches asynchrones en arrière-plan (scheduled_tasks.json) et système de notifications push natives Windows (via PowerShell Toast).

Vision Agent : Capture et analyse sémantique multimodale de l'écran en direct via Pillow et Gemini 1.5.

🌐 3. Orba OS Website
Plateforme : Web (HTML5, Vanilla CSS, JS).

Objectif : Vitrine technologique interactive présentant le projet, sa feuille de route (Roadmap interactive), ses phases de déploiement et ses liens de téléchargement.

🔒 Charte de Souveraineté & de Sécurité
Chaque application de l'écosystème Orba respecte trois piliers fondamentaux :

Priorité au Local (Offline-First) : Les modèles LLM locaux (via Ollama sur PC ou modèles optimisés sur Mobile) et les modèles STT/TTS (Vosk, Piper) sont privilégiés pour garantir la confidentialité absolue de vos données.

Transparence des Décisions (ReAct Log) : L'agent affiche ouvertement ses "pensées" (thoughts) et les outils qu'il s'apprête à accomplir, évitant l'effet "boîte noire".

Contrôle Utilisateur (Zero-Trust Guardrails) : Aucune modification critique (suppression, modification de fichiers système, exécution de scripts) ne peut être effectuée sans une approbation explicite (bouton à l'écran ou réponse par mot-clé SMS/WhatsApp).

## 🇬🇧 English Version

Welcome to The Orba Ecosystem, a software suite of sovereign, cognitive, secure, and multimodal personal assistants. This ecosystem unifies the intelligent agent experience across all your devices, from mobile smartphones to desktop computers.

🗺️ Ecosystem Architecture
The ecosystem coordinates three complementary and interconnected components:


```mermaid
graph TD
    A["ORBA ECOSYSTEM (Souverain & Agentique)"] --> B["Orba OS Mobile (Android App)"]
    A --> C["Orba OS Desktop (Tauri / FastAPI)"]
    A --> D["Orba OS Website (Landing Page Showcase)"]

    B --> B1["Modèle Local JNI C++ / Kotlin"]
    B --> B2["Synthèse Vocale locale (Piper JNI)"]
    B --> B3["OrbaSphere Mobile UI"]

    C --> C1["Boucle Cognitive ReAct Python"]
    C --> C2["Visualiseur WebGL / Canvas"]
    C --> C3["Gateways (Micro local, Telegram, WhatsApp)"]

    D --> D1["Roadmap Interactive"]
    D --> D2["Aesthetics V3 Glassmorphism"]


🛠️ Project Components
📱 1. Orba OS Mobile
Platform: Android (Native Kotlin, C++ NDK).

Objective: A secure pocket assistant designed to run fully offline on the smartphone's Neural Processing Unit (NPU).

Key Features:

Local speech recognition and synthesis via the JNI integration of Piper TTS.

Asynchronous synchronization of audio streams combined with advanced RAM optimization.

Manual Local Import: Built-in system picker to manually import models (gemma.bin and Piper voices) entirely offline.

Normalized Voice Classifier: Tokenization and intent classification built to be accent-resilient using strict Unicode normalization.

🖥️ 2. Orba OS Desktop
Platform: Windows, macOS, Linux (Tauri v2 / FastAPI / Python).

Objective: A floating, autonomous desktop companion capable of executing system tasks securely on your computer.

Key Features:

OrbaSphere: A transparent, borderless WebGL circular widget floating smoothly above your workspace.

Guardrails System (Human-in-the-loop): Automatic interception of critical system commands, halting operations until explicit user authorization is granted.

Multi-Channel Gateways: Remote orchestration and verification via Telegram or WhatsApp (powered by Twilio).

Local STT & TTS: Offline Vosk (recognition) and Piper (speech) engines with real-time visual syncing based on audio level (RMS).

Scheduler & Notifications: Background asynchronous task loop (scheduled_tasks.json) hooked into native system push notifications (via Windows PowerShell Toast).

Vision Agent: Multimodal semantic capture and real-time screen analysis using Pillow and Gemini 1.5.

🌐 3. Orba OS Website
Platform: Web (HTML5, Vanilla CSS, JS).

Objective: An interactive showcase website displaying the project's vision, interactive roadmap, deployment phases, and download links.

🔒 Sovereignty & Security Charter
Every application within the Orba ecosystem is built upon three unyielding pillars:

Local-First Priority: Local LLMs (via Ollama on desktop or optimized architectures on mobile) and local STT/TTS engines (Vosk, Piper) are strictly prioritized to ensure absolute data privacy.

Decision Transparency (ReAct Log): The agent breaks the traditional "black box" effect by openly displaying its internal thoughts, logical reasoning, and the tools it plans to invoke before acting.

User Control (Zero-Trust Guardrails): No critical system changes (file modification, deletion, script execution) can occur without explicit user consent, validated either locally on-screen or remotely via encrypted WhatsApp/Telegram keywords.

Decision Transparency (ReAct Log): The agent breaks the traditional "black box" effect by openly displaying its internal thoughts, logical reasoning, and the tools it plans to invoke before acting.

User Control (Zero-Trust Guardrails): No critical system changes (file modification, deletion, script execution) can occur without explicit user consent, validated either locally on-screen or remotely via encrypted WhatsApp/Telegram keywords.
