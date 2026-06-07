# 🤝 Contribution à Orba OS / Contributing to Orba OS

[🇫🇷 Français](#français) | [🇬🇧 English](#english)

<a name="français"></a>
## 🇫🇷 Français

Nous sommes ravis que vous souhaitiez contribuer à **Orba OS** ! L'écosystème est ouvert aux améliorations, corrections de bugs et nouvelles idées.

En contribuant à ce projet, vous acceptez que vos contributions soient placées sous la licence **Apache 2.0** du projet.

---

### 🐛 Signaler un Problème ou Suggérer une Fonctionnalité

Avant de soumettre du code, nous vous encourageons à ouvrir une **Issue** sur GitHub pour en discuter :
1. Recherchez si une issue similaire existe déjà.
2. Si ce n'est pas le cas, créez une nouvelle issue en expliquant clairement le problème rencontré ou la fonctionnalité souhaitée.
3. Donnez un maximum de détails pour faciliter la reproduction (OS, logs, étapes, etc.).

---

### 🛠️ Contribuer avec du Code (Pull Requests)

Voici la procédure standard pour proposer des modifications :

1. **Forker le projet** sur votre compte GitHub.
2. **Cloner votre fork** en local :
   ```bash
   git clone https://github.com/VOTRE_USERNAME/ORBA_OS.git
   ```
3. **Créer une branche** descriptive pour vos modifications :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   # ou
   git checkout -b fix/correctif-bug
   ```
4. **Développer et tester** vos modifications :
   - Assurez-vous que l'application compile sans erreur.
   - Ajoutez des tests si nécessaire.
5. **Committer vos changements** avec un message clair :
   ```bash
   git commit -m "feat: ajout de la prise en charge de..."
   ```
6. **Pousser votre branche** sur votre fork :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
7. **Ouvrir une Pull Request (PR)** sur le dépôt principal en décrivant en détail vos changements.

---

### 🎨 Normes de Code

Pour assurer la cohérence et la qualité du code de l'écosystème :

#### 📱 Orba OS Mobile (Android / Kotlin)
- Adhérez aux standards de codage Kotlin et Jetpack Compose.
- Veillez à ne pas introduire de fuites de mémoire (particulièrement avec Piper TTS ou LiteRT/Gemma).
- Commentez les sections complexes en C++ (JNI).

#### 🖥️ Orba OS Desktop (Tauri / FastAPI / Web)
- Suivez les standards PEP 8 pour le code Python (FastAPI).
- Gardez le code frontend (WebGL / Canvas) optimisé (mise en veille de la boucle d'animation lorsque la fenêtre est inactive).
- Respectez la structure de Guardrails (les actions système critiques doivent toujours passer par l'orchestrateur de sécurité).

<br>

<a name="english"></a>
## 🇬🇧 English

We are thrilled that you want to contribute to **Orba OS**! The ecosystem is open to improvements, bug fixes, and new ideas.

By contributing to this project, you agree that your contributions will be licensed under the project's **Apache 2.0** license.

---

### 🐛 Report a Bug or Suggest a Feature

Before submitting code, we encourage you to open an **Issue** on GitHub to discuss it:
1. Check if a similar issue already exists.
2. If not, create a new issue clearly explaining the problem encountered or the desired feature.
3. Provide as many details as possible to facilitate reproduction (OS, logs, steps, etc.).

---

### 🛠️ Contribute Code (Pull Requests)

Here is the standard procedure for proposing changes:

1. **Fork the project** to your GitHub account.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ORBA_OS.git
   ```
3. **Create a descriptive branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/bug-fix
   ```
4. **Develop and test** your changes:
   - Ensure the application compiles without errors.
   - Add tests if necessary.
5. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add support for..."
   ```
6. **Push your branch** to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
7. **Open a Pull Request (PR)** on the main repository describing your changes in detail.

---

### 🎨 Coding Standards

To ensure the consistency and quality of the ecosystem's code:

#### 📱 Orba OS Mobile (Android / Kotlin)
- Adhere to Kotlin and Jetpack Compose coding standards.
- Be careful not to introduce memory leaks (especially with Piper TTS or LiteRT/Gemma).
- Comment complex sections in C++ (JNI).

#### 🖥️ Orba OS Desktop (Tauri / FastAPI / Web)
- Follow PEP 8 standards for Python code (FastAPI).
- Keep frontend code (WebGL / Canvas) optimized (pause the animation loop when the window is inactive).
- Respect the Guardrails structure (critical system actions must always pass through the security orchestrator).

Auteur / Author: Alex Koncept — contact@alexkoncept.com  
Portfolio: https://alexkoncept.github.io/

Voir aussi : CODE_OF_CONDUCT.md, SECURITY.md, .github/ISSUE_TEMPLATE/

## Avant de proposer une modification
- Ouvrez une issue pour discuter de la fonctionnalité ou du bug.
- Assurez-vous de suivre le Code of Conduct.

## Pull Requests
- Fork -> branche descriptive -> PR vers main.
- Incluez des tests si possible et mettez à jour le CHANGELOG.

## Vérifications recommandées avant PR
- Kotlin: ktlint / detekt selon la partie du code
- Python: black, flake8, mypy
- JS: eslint
- Android: ./gradlew lint

## Communication
- Contact principal : contact@alexkoncept.com
- Auteur: Alex Koncept — https://alexkoncept.github.io/
