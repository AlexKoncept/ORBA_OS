# Contributing to Orba OS Mobile 

Thank you for your interest in contributing to **Orba OS v3**! We welcome and appreciate contributions of all kinds, including bug fixes, new tools, feature requests, and documentation improvements.

---

## 🛠️ How to Contribute

### 1. Find or Create an Issue
Before starting work, please search the existing issues or create a new one to discuss the changes you would like to make. This helps avoid duplicate work and ensures the proposed changes align with the project's vision.

### 2. Set Up the Development Environment
1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ORBA_OS_Mobile.git
   ```
3. Set up **Android Studio** (Koala or newer recommended).
4. Install the **Android NDK** and **CMake** from the SDK Manager to build the native Piper C++ components.

### 3. Implement Your Changes
* Create a new branch for your work (e.g., `feature/my-awesome-tool` or `fix/issue-123`).
* Keep your commits atomic, clear, and descriptive.
* Follow the project's code style (Kotlin for Android, Modern C++ for Piper native bridge).

### 4. Verify Your Code
Before submitting your changes, run the following checks locally:
* **Code Formatting**: Fix and verify formatting automatically using Spotless:
  ```bash
  ./gradlew spotlessApply
  ```
* **Local Tests**: Ensure all unit tests run and pass successfully:
  ```bash
  ./gradlew testDemoDebug
  ```

### 5. Submit a Pull Request
1. Push your changes to your fork:
   ```bash
   git push origin feature/my-awesome-tool
   ```
   *Note: Please fill out the pull request template description when opening your PR.*
2. Open a Pull Request from your branch to the main repository.

---

## 📬 Contact & Support

If you have any questions, suggestions, or want to discuss structural changes to the project, feel free to reach out:
* **Creator**: Alex Koncept
* **Email**: [contact@th-group.eu](mailto:contact@th-group.eu)
* **Portfolio**: [alexkoncept.github.io](https://alexkoncept.github.io/)
