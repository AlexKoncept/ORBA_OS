package com.google.samples.apps.nowinandroid.tools

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ModelDownloader @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val modelsDir = File(context.filesDir, "models")
    
    // Status can be: CHECKING, NEED_DOWNLOAD, DOWNLOADING, READY
    private val _downloadState = MutableStateFlow("CHECKING")
    val downloadState: StateFlow<String> = _downloadState

    private val _progress = MutableStateFlow(0f)
    val progress: StateFlow<Float> = _progress

    init {
        if (!modelsDir.exists()) {
            modelsDir.mkdirs()
        }
    }

    fun checkModels() {
        val gemmaFile = File(modelsDir, "gemma.bin")
        val piperFile = File(modelsDir, "fr_FR-siwis-medium.onnx")

        if (gemmaFile.exists() && piperFile.exists()) {
            _downloadState.value = "READY"
        } else {
            _downloadState.value = "NEED_DOWNLOAD"
        }
    }

    fun startDownload() {
        _downloadState.value = "DOWNLOADING"
        // Ceci est une simulation d'interface de téléchargement.
        // Dans le vrai projet, utiliser DownloadManager ou Ktor pour télécharger depuis le serveur.
        
        Log.i("ModelDownloader", "Lancement du téléchargement des modèles IA...")
        // Thread simulant le téléchargement progressif
        Thread {
            for (i in 1..100) {
                Thread.sleep(50) // Simulation
                _progress.value = i / 100f
            }
            
            // Simulation de la création des fichiers (pour passer le check)
            File(modelsDir, "gemma.bin").createNewFile()
            File(modelsDir, "fr_FR-siwis-medium.onnx").createNewFile()
            
            _downloadState.value = "READY"
        }.start()
    }

    fun isGemmaPresent(): Boolean {
        return File(modelsDir, "gemma.bin").exists()
    }

    fun isPiperPresent(): Boolean {
        return File(modelsDir, "fr_FR-siwis-medium.onnx").exists()
    }

    suspend fun importModel(uri: Uri, modelName: String): Boolean = withContext(Dispatchers.IO) {
        try {
            if (!modelsDir.exists()) {
                modelsDir.mkdirs()
            }
            val destFile = File(modelsDir, modelName)
            context.contentResolver.openInputStream(uri)?.use { inputStream ->
                destFile.outputStream().use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
            }
            checkModels()
            true
        } catch (e: Exception) {
            Log.e("ModelDownloader", "Erreur lors de l'importation de $modelName", e)
            false
        }
    }
}
