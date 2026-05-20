# Orba OS v3

**Orba OS** est un système d'intelligence personnelle souverain, modulaire et local conçu pour s'exécuter directement au-dessus d'Android. Inspiré par la vision d'un compagnon virtuel intime (comme dans le film *Her*), Orba OS est l'évolution directe du projet **Orba**. Il garantit une confidentialité absolue (Zero-Cloud, 100% Offline-First) et une réactivité matérielle maximale.

---

## 🌌 Vision du Projet
Orba OS ne se contente pas d'être une simple application de chatbot ; il s'agit d'une couche d'intelligence invisible qui interagit avec le monde réel et le matériel de votre téléphone :
1. **Zéro Serveur** : Toutes les données personnelles, transcriptions et modélisations vocales restent et s'exécutent sur l'appareil.
2. **Proactivité** : Grâce à un service d'arrière-plan permanent, Orba peut initier des interactions, envoyer des alertes ou adapter son comportement selon vos habitudes locales.
3. **Réactivité Sensorielle** : L'interface utilisateur est matérialisée par l'**OrbaSphere**, un orbe 3D organique généré par Shaders AGSL qui pulse en temps réel en fonction de l'amplitude de votre voix.

---

## 🛠️ Architecture & Pipeline Technique
Le projet s'appuie sur une pile moderne mariant le développement Android moderne (inspiré de la structure *Now in Android*) et la compilation native C++ pour les performances de pointe.

```mermaid
graph TD
    A[Microphone STT] -->|RMS volume & Transcription| B[OrbaViewModel]
    B -->|Requête Vocale| C[OrbaAgentManager]
    C -->|Regex Matching| D[AndroidSystemTool]
    D -->|Commande Matérielle| E[OS Android / Flashlight / Battery]
    E -->|Retour Statut| C
    C -->|Contexte Injecté| F[OrbaBrain LiteRT / Gemma-2B-IT]
    F -->|Texte Nettoyé| G[OrbaVoice C++ Piper TTS]
    G -->|Flux PCM Direct| H[AudioTrack Mobile]
    H -->|Fin de Parole| B
    B -->|Relance Écoute| A
```

### 1. Orba Core (Le Cerveau LLM)
*   **Modèle** : Google Gemma-2B-IT (Instruction-tuned).
*   **Technologie** : Inférence sémantique locale exécutée via **LiteRT** (anciennement TensorFlow Lite), optimisée pour exploiter les accélérateurs matériels mobiles (GPU/NPU).
*   **Fichier clé** : `OrbaBrain.kt`

### 2. Orba Voice (Le Pipeline Audio)
*   **Speech-To-Text (STT)** : Reconnaissance vocale locale en continu gérée par le moteur natif Android (`OrbaSpeechRecognizer.kt`) en mode déconnecté. Le volume RMS (décibels) de la voix est capturé à la source et exposé dans un flux `StateFlow` réactif.
*   **Text-To-Speech (TTS)** : Moteur de synthèse vocale neuronale rapide **Piper** écrit en C++ natif et chargé via JNI (`piper_jni.cpp`). Piper lit la réponse sémantique en générant un flux PCM direct injecté dans une piste `AudioTrack` pour une sortie vocale instantanée et chaleureuse.

### 3. Orba UI (OrbaSphere Shaders)
*   **Technologie** : AGSL (Android Graphics Shading Language).
*   **Fonctionnement** : Un shader personnalisé simule un plasma volumétrique de couleur Rose/Magenta en mode veille. Lors de la parole, le shader intercepte les décibels RMS vocaux pour faire osciller l'amplitude et la fréquence du plasma en temps réel.
*   **Fichier clé** : `OrbaSphere.kt`

### 4. Orba Agents & Orba Flow (Les Outils Android)
*   **OrbaAgentManager** : Intercepte les demandes vocales avant de les envoyer au LLM et détermine si une action matérielle doit être exécutée.
*   **AndroidSystemTool** : Pilote directement le smartphone hors-ligne. Il permet de :
    *   Vérifier le niveau de la batterie.
    *   Activer ou désactiver la lampe torche.
    *   Basculer en mode silencieux / vibration (AudioManager).
    *   Programmer une alarme physique ou obtenir l'heure système.
    *   Lancer des recherches web locales par Intent ou ouvrir des applications (YouTube, Gmail, Maps, Appareil photo, Paramètres Bluetooth/Wi-Fi).

### 5. Orba Memory (Mémoire Souveraine)
*   Persistance locale via **Jetpack DataStore** (`OrbaMemory.kt`) stockant de manière cryptée le prénom de l'utilisateur et son contexte pour personnaliser l'inférence locale.

### 6. Orba Proactive (Service d'Arrière-Plan)
*   **OrbaProactiveService** : Un Foreground Service persistant Android qui exécute une boucle d'analyse de contexte locale en arrière-plan et déclenche de manière proactive des notifications vocales ou écrites sans intervention utilisateur.

---

## 🏗️ Fiche Technique & Prérequis

### Configuration Minimale Requise :
*   **OS Android** : Android 13.0 (API Level 33) ou supérieur (requis pour les shaders AGSL et les API audio).
*   **Matériel** : Processeur Octa-core avec un minimum de **6 Go de RAM** (pour conserver Gemma-2B et le moteur Piper TTS chargés en mémoire sans interruption par le système OOM Killer).

### Déploiement & Compilation C++ :
Pour compiler le projet depuis ses sources, vous devez installer dans **Android Studio** :
1.  Le **NDK (Side-by-side)** (Native Development Kit).
2.  Le compilateur **CMake**.
3.  Ouvrez le projet et sélectionnez la variante de build `demoDebug`.
4.  Assurez-vous de configurer le fichier C++ Piper (`CMakeLists.txt` et `piper_jni.cpp`) pour lier correctement les bibliothèques statiques Piper et ONNX Runtime.

---

## 📲 Processus de Premier Boot (ModelDownloader)
L'APK généré par compilation est volontairement léger (~30Mo) pour optimiser les temps de build et de déploiement.
Lors du premier lancement de l'application :
1.  Un écran de garde `ModelDownloader` s'affiche et initie un téléchargement asynchrone sécurisé vers l'appareil.
2.  **Modèle Gemma-2B-IT** : Téléchargement et quantisation en local (~2.5 Go).
3.  **Voix Piper (Français)** : Téléchargement du fichier `.onnx` de voix et de sa configuration `.json` (~50 Mo).
4.  Les fichiers sont stockés dans le répertoire chiffré privé `context.filesDir` et chargés directement en RAM lors des lancements suivants.

---

## 📄 Licence
Ce projet est distribué sous licence **Apache License 2.0**.
Consultez le fichier `LICENSE` pour plus de détails.

---
*Projet conçu, écrit et imaginé par **Alex Koncept**.*
