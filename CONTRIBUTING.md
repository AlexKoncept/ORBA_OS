# 🤝 Contribution à Orba OS

Nous sommes ravis que vous souhaitiez contribuer à **Orba OS** ! L'écosystème est ouvert aux améliorations, corrections de bugs et nouvelles idées.

En contribuant à ce projet, vous acceptez que vos contributions soient placées sous la licence **Apache 2.0** du projet.

---

## 🐛 Signaler un Problème ou Suggérer une Fonctionnalité

Avant de soumettre du code, nous vous encourageons à ouvrir une **Issue** sur GitHub pour en discuter :
1. Recherchez si une issue similaire existe déjà.
2. Si ce n'est pas le cas, créez une nouvelle issue en expliquant clairement le problème rencontré ou la fonctionnalité souhaitée.
3. Donnez un maximum de détails pour faciliter la reproduction (OS, logs, étapes, etc.).

---

## 🛠️ Contribuer avec du Code (Pull Requests)

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

## 🎨 Normes de Code

Pour assurer la cohérence et la qualité du code de l'écosystème :

### 📱 Orba OS Mobile (Android / Kotlin)
- Adhérez aux standards de codage Kotlin et Jetpack Compose.
- Veillez à ne pas introduire de fuites de mémoire (particulièrement avec Piper TTS ou LiteRT/Gemma).
- Commentez les sections complexes en C++ (JNI).

### 🖥️ Orba OS Desktop (Tauri / FastAPI / Web)
- Suivez les standards PEP 8 pour le code Python (FastAPI).
- Gardez le code frontend (WebGL / Canvas) optimisé (mise en veille de la boucle d'animation lorsque la fenêtre est inactive).
- Respectez la structure de Guardrails (les actions système critiques doivent toujours passer par l'orchestrateur de sécurité).
