# Audit de Qualité, Architecture et Sécurité — Orba OS v3

*   **Date d'évaluation** : 19 Mai 2026
*   **Version du Projet** : v3.0-Edge
*   **Périmètre audité** : Architecture Kotlin (Hilt/ViewModel), Liaisons Natives C++ JNI (Piper TTS), Gestionnaire d'Agents (`OrbaAgentManager`), Permissions Système et Service d'arrière-plan (`OrbaProactiveService`).

---

## 1. Objectifs de l'Audit

Cet audit vise à évaluer la conformité de l'implémentation logicielle d'Orba OS avec ses promesses techniques phares :
1.  **Souveraineté et vie privée** (100% Offline-First, Zero-Cloud).
2.  **Modularité** (Pipeline Agentique découplé via `OrbaTool`).
3.  **Performances et gestion mémoire** (Inférence hybride CPU/GPU/NPU locale via LiteRT et Piper C++).
4.  **Stabilité concurrentielle** (Gestion de la parole, de l'écoute et du rendu graphique AGSL).

---

## 2. Audit de l'Architecture & Flux de Données

### Conception Globale (Kotlin & MVVM)
*   **Points Forts** :
    *   L'intégration de **Hilt** pour l'injection de dépendances garantit une instanciation propre et unique de `OrbaBrain` et `OrbaVoice` à l'échelle de l'application ou du service d'arrière-plan.
    *   L'architecture découplée entre `OrbaSpeechRecognizer` (STT), `OrbaVoice` (TTS) et `OrbaBrain` (LLM) permet une maintenance et un remplacement aisé de chaque brique.
*   **Synchronisation du Pipeline Conversationnel** :
    *   *Avant* : Risques de chevauchement où le microphone écoutait sa propre synthèse vocale (Piper), provoquant des boucles de feedback et des hallucinations.
    *   *Correction validée* : La boucle d'écoute STT est désormais verrouillée et n'est relancée de manière synchrone par le `OrbaViewModel` qu'après réception de l'événement de fin de lecture de la synthèse vocale Piper.

### OrbaAgentManager & AndroidSystemTool (Pipeline d'action)
*   **Points Forts** :
    *   L'utilisation de `AndroidSystemTool` pour manipuler le matériel (lampe torche, AudioManager, batterie) via des Intents Android locaux est propre et ne nécessite aucune API tierce.
    *   L'interception des intentions via Regex dans `OrbaAgentManager` permet de court-circuiter l'inférence LLM pour les requêtes système standards (ex: "allume la lampe"). Cela préserve la batterie et élimine la latence d'inférence.
*   **Piste d'amélioration** :
    *   Les Regex sont efficaces mais rigides pour le langage naturel complexe. *Recommandation* : Introduire un classifieur sémantique léger (type MobileBERT de quelques Mo ou une grammaire structurée Gemma) pour mieux classifier les intentions sans dépendre uniquement de correspondances strictes de mots-clés.

---

## 3. Audit de Sécurité & Confidentialité (Privacy)

*   **Audit Offline-First** : **Vérifié et validé**. Le code d'inférence de `OrbaBrain` (LiteRT) et `OrbaVoice` (JNI C++) ne réalise aucun appel réseau. Les données de conversation restent dans la mémoire RAM volatile de l'application.
*   **Permissions Android** :
    *   Le microphone utilise `RECORD_AUDIO` qui requiert une approbation utilisateur explicite au runtime.
    *   Le service permanent utilise `FOREGROUND_SERVICE` conformément aux règles de l'API Android 33+ (nécessite l'affichage d'une notification persistante pour avertir l'utilisateur).
    *   L'accès au mode silencieux utilise `ACCESS_NOTIFICATION_POLICY`, garantissant que le système restreint le contrôle du volume matériel aux applications explicitement autorisées.
*   **Piste de renforcement de sécurité** :
    *   La permission `INTERNET` est déclarée dans le Manifeste pour permettre le téléchargement initial des modèles (`ModelDownloader`). Une fois les modèles stockés dans le répertoire chiffré `context.filesDir`, l'application n'a techniquement plus besoin d'internet.
    *   *Recommandation* : Séparer le module de téléchargement initial dans un processus ou une étape distincte, ou utiliser des configurations réseau Android strictes (`networkSecurityConfig`) pour bloquer toute tentative d'exfiltration de données par le LLM local.

---

## 4. Audit de Code et Liaison Native JNI C++ (Piper TTS)

Le cœur de la synthèse vocale s'appuie sur le code C++ compilé via CMake dans `piper_jni.cpp`.

*   **Thread-Safety & Concurrence** :
    *   **Validé** : L'utilisation d'un verrou `std::mutex` dans le wrapper JNI protège le synthétiseur Piper contre les appels de synthèse concurrents. Cela évite les corruptions de mémoire et les plantages fatals de la JVM (Signal 11 / Segmentation Fault) en cas de requêtes vocales ultra-rapides.
*   **Gestion de la RAM (Inférence Locale)** :
    *   Le chargement de Gemma-2B-IT (~2.5 Go) combiné à Piper Voice ONNX (~50 Mo) génère une empreinte RAM élevée au démarrage.
    *   Le système de gestion de mémoire Android (Low Memory Killer) risque de tuer l'application si l'utilisateur ouvre un jeu gourmand en arrière-plan.
    *   *Recommandation* : Implémenter une libération intelligente des ressources (déchargement de Gemma) dans le cycle de vie de l'application (`onTrimMemory` ou `onStop`) tout en conservant le service persistant `OrbaProactiveService` en veille légère.

---

## 5. Synthèse des Recommandations (Matrice d'Action)

| Priorité | Domaine | Description | Solution Recommandée |
| :--- | :--- | :--- | :--- |
| **Haute** | RAM / Cycle de vie | Risque de fermeture par le système Android (Low Memory Killer) due à l'inférence locale en RAM. | Implémenter la méthode `onTrimMemory` pour libérer le cache de Gemma quand l'application n'est plus au premier plan. |
| **Moyenne** | Sécurité | Sécurisation du transport des modèles et isolation réseau. | Configurer un fichier `network-security-config` bloquant tout trafic sortant non chiffré ou non validé. |
| **Moyenne** | Intelligence | Rigidité des filtres Regex dans `OrbaAgentManager`. | Migrer vers une classification d'intentions via tokens sémantiques ou classifieur On-Device léger. |
| **Faible** | UI / Expérience | Fluidité de l'OrbaSphere sur les appareils d'entrée de gamme. | Proposer une option dans les paramètres pour réduire la résolution ou le nombre de points du shader AGSL (mode économie d'énergie). |

---
*Audit réalisé par l'assistant IA Antigravity pour le projet **Orba OS** par **Alex Koncept**.*
