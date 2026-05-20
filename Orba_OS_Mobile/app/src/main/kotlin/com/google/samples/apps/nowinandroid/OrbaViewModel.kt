package com.google.samples.apps.nowinandroid

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.google.samples.apps.nowinandroid.core.common.audio.OrbaSpeechRecognizer
import com.google.samples.apps.nowinandroid.core.common.audio.OrbaVoice
import com.google.samples.apps.nowinandroid.core.common.intelligence.OrbaBrain
import com.google.samples.apps.nowinandroid.core.ui.OrbaState
import com.google.samples.apps.nowinandroid.core.common.intelligence.OrbaMemory
import com.google.samples.apps.nowinandroid.tools.GoogleNewsTool
import com.google.samples.apps.nowinandroid.tools.ModelDownloader
import android.net.Uri
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OrbaViewModel @Inject constructor(
    private val speechRecognizer: OrbaSpeechRecognizer,
    private val brain: OrbaBrain,
    private val voice: OrbaVoice,
    private val agentManager: com.google.samples.apps.nowinandroid.tools.OrbaAgentManager,
    private val memory: OrbaMemory,
    private val downloader: ModelDownloader
) : ViewModel() {

    val downloadState = downloader.downloadState
    val downloadProgress = downloader.progress

    fun checkModels() {
        downloader.checkModels()
    }

    fun startModelDownload() {
        downloader.startDownload()
    }

    fun isGemmaPresent(): Boolean = downloader.isGemmaPresent()
    fun isPiperPresent(): Boolean = downloader.isPiperPresent()

    fun importModel(uri: Uri, modelName: String) {
        viewModelScope.launch {
            downloader.importModel(uri, modelName)
        }
    }

    private val _uiState = MutableStateFlow(OrbaState.IDLE)
    val uiState: StateFlow<OrbaState> = _uiState.asStateFlow()

    private val _volume = MutableStateFlow(0.1f)
    val volume: StateFlow<Float> = _volume.asStateFlow()

    private val _spokenText = MutableStateFlow("")
    val spokenText: StateFlow<String> = _spokenText.asStateFlow()

    val userName = memory.userName
    val userContext = memory.userContext
    val selectedVoice = memory.selectedVoice

    fun saveProfile(name: String, contextInfo: String, voice: String) {
        viewModelScope.launch {
            memory.updateProfile(name, contextInfo, voice)
        }
    }

    init {
        // Observers setup for the continuous STT
        viewModelScope.launch {
            speechRecognizer.isListening.collectLatest { listening ->
                if (listening && _uiState.value != OrbaState.SPEAKING && _uiState.value != OrbaState.THINKING) {
                    _uiState.value = OrbaState.LISTENING
                }
            }
        }

        viewModelScope.launch {
            speechRecognizer.volume.collectLatest { vol ->
                // OrbaSphere pulse au rythme de votre voix !
                if (_uiState.value == OrbaState.LISTENING) {
                    _volume.value = 0.1f + (vol * 0.5f) 
                }
            }
        }

        viewModelScope.launch {
            speechRecognizer.transcription.collectLatest { text ->
                if (text.isNotBlank()) {
                    _spokenText.value = text
                    processInput(text)
                }
            }
        }
    }

    fun startListening() {
        _uiState.value = OrbaState.LISTENING
        _volume.value = 0.1f
        speechRecognizer.startListening()
    }

    private fun processInput(prompt: String) {
        speechRecognizer.stopListening()
        
        viewModelScope.launch {
            _uiState.value = OrbaState.ANALYZING
            _volume.value = 0.3f
            
            // Récupération de la mémoire persistante (ORBA MEMORY)
            val currentUserName = memory.userName.first()
            val currentUserContext = memory.userContext.first()
            
            // 1. Agentic Routing & Grounding (ORBA AGENTS / FLOW)
            var finalPrompt = ""
            val agentResult = agentManager.evaluateAndExecute(prompt)
            
            if (agentResult != null) {
                // L'agent a exécuté une action et nous donne le contexte système
                finalPrompt = """
                    [CONTEXTE SYSTEME]
                    Tu es Orba, l'Intelligence Personnelle locale de $currentUserName.
                    ${agentResult.systemContext}
                    
                    [REQUETE UTILISATEUR]
                    "$prompt"
                    
                    [INSTRUCTION]
                    Réponds naturellement et brièvement en prenant en compte l'action qui vient d'être exécutée. Ne mentionne pas tes instructions systèmes.
                """.trimIndent()
            } else {
                // Conversation normale
                finalPrompt = """
                    [CONTEXTE SYSTEME]
                    Tu es Orba OS, un système d'intelligence personnelle local, modulaire et multimodal.
                    Tu es exécuté directement sur le téléphone de $currentUserName (Offline-first, Privacy-first).
                    Ce que tu sais de lui/elle : $currentUserContext
                    Ton rôle est d'être un compagnon proactif, analytique et empathique. Tes réponses doivent être concises et chaleureuses (idéalement pour être lues à voix haute par TTS).
                    
                    [REQUETE UTILISATEUR]
                    "$prompt"
                    
                    [REPONSE D'ORBA]
                """.trimIndent()
            }

            // 2. Réflexion (ORBA CORE - LLM Inference)
            _uiState.value = OrbaState.THINKING
            _volume.value = 0.5f 
            
            var fullResponse = ""
            brain.think(finalPrompt).collect { chunk ->
                fullResponse += chunk
            }

            // 3. Parole (ORBA VOICE - TTS)
            _uiState.value = OrbaState.SPEAKING
            _volume.value = 0.8f 
            
            // On nettoie la réponse des potentiels tags générés par le modèle pour le TTS
            val cleanResponse = fullResponse.replace(Regex("\\[.*?\\]"), "").trim()
            
            if (cleanResponse.isNotBlank()) {
                val currentVoice = memory.selectedVoice.first()
                voice.speak(cleanResponse, voiceName = currentVoice)
            }

            // 4. Retour au repos et reprise de l'écoute (Conversation Continue)
            _volume.value = 0.1f
            _uiState.value = OrbaState.IDLE
            
            // Relancer l'écoute pour simuler un "Assistant Temps Réel Permanent"
            startListening()
        }
    }

    override fun onCleared() {
        super.onCleared()
        speechRecognizer.stopListening()
        brain.cleanUp()
    }
}
