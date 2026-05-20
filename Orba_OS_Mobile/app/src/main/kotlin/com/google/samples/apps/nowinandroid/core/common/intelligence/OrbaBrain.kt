package com.google.samples.apps.nowinandroid.core.common.intelligence

import android.content.Context
import android.util.Log
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.Content
import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.Conversation
import com.google.ai.edge.litertlm.ConversationConfig
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.google.ai.edge.litertlm.Message
import com.google.ai.edge.litertlm.MessageCallback
import com.google.ai.edge.litertlm.SamplerConfig
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OrbaBrain @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val tag = "OrbaBrain"
    private var engine: Engine? = null
    private var conversation: Conversation? = null

    // Le modèle sera stocké dans la mémoire interne de l'application
    private val modelPath = File(context.filesDir, "models/gemma.bin").absolutePath

    fun initialize(): Boolean {
        if (!File(modelPath).exists()) {
            Log.e(tag, "Le modèle Gemma n'est pas présent à l'emplacement : $modelPath")
            return false
        }

        try {
            val engineConfig = EngineConfig(
                modelPath = modelPath,
                backend = Backend.GPU(), // Using GPU acceleration by default for best performance
                maxNumTokens = 1024
            )

            engine = Engine(engineConfig).apply {
                initialize()
            }

            val conversationConfig = ConversationConfig(
                samplerConfig = SamplerConfig(
                    topK = 40,
                    topP = 0.95,
                    temperature = 0.8
                )
            )

            conversation = engine?.createConversation(conversationConfig)
            Log.i(tag, "Orba Brain (Gemma) Initialisé avec succès.")
            return true
        } catch (e: Exception) {
            Log.e(tag, "Erreur lors de l'initialisation du cerveau Orba", e)
            return false
        }
    }

    /**
     * Envoie une requête au modèle et retourne un Flow contenant la réponse en streaming.
     */
    fun think(prompt: String): Flow<String> = callbackFlow {
        if (conversation == null) {
            val initSuccess = initialize()
            if (!initSuccess) {
                trySend("Erreur : Le cerveau d'Orba n'est pas connecté ou le modèle est manquant.")
                close()
                return@callbackFlow
            }
        }

        val contents = Contents.of(Content.Text(prompt))

        conversation?.sendMessageAsync(
            contents,
            object : MessageCallback {
                override fun onMessage(message: Message) {
                    // Send stream chunks to the flow
                    trySend(message.toString())
                }

                override fun onDone() {
                    close()
                }

                override fun onError(throwable: Throwable) {
                    Log.e(tag, "Erreur de réflexion", throwable)
                    trySend("Erreur de cognition : ${throwable.message}")
                    close(throwable)
                }
            }
        )

        awaitClose {
            // Optional: cancel process if flow is cancelled
            conversation?.cancelProcess()
        }
    }

    fun cleanUp() {
        try {
            conversation?.close()
            engine?.close()
        } catch (e: Exception) {
            Log.e(tag, "Erreur lors du nettoyage de la mémoire.", e)
        } finally {
            conversation = null
            engine = null
        }
    }
}
