package com.google.samples.apps.nowinandroid.core.common.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.util.Log
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OrbaVoice @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val tag = "OrbaVoice"

    init {
        try {
            System.loadLibrary("piper_jni")
        } catch (e: UnsatisfiedLinkError) {
            Log.e(tag, "La librairie native Piper n'a pas pu être chargée.", e)
        }
    }

    private external fun synthesizeText(text: String, modelPath: String): ByteArray

    suspend fun speak(text: String, voiceName: String = "Kore") {
        withContext(Dispatchers.IO) {
            try {
                Log.i(tag, "Orba réfléchit à la prononciation...")
                
                val modelsDir = File(context.filesDir, "models").absolutePath
                val modelPath = when (voiceName) {
                    "Kore" -> "$modelsDir/fr_FR-siwis-medium.onnx"
                    "Puck" -> "$modelsDir/fr_FR-upmc-medium.onnx"
                    "Charon" -> "$modelsDir/fr_FR-tom-medium.onnx"
                    "Zephyr" -> "$modelsDir/fr_FR-gilles-low.onnx"
                    "Fenrir" -> "$modelsDir/fr_FR-bruno-low.onnx"
                    else -> "$modelsDir/fr_FR-siwis-medium.onnx"
                }

                val pcmAudioData = synthesizeText(text, modelPath)
                
                if (pcmAudioData.isEmpty()) {
                    Log.e(tag, "Le moteur Piper a renvoyé un flux audio vide.")
                    return@withContext
                }

                // 2. Configuration du lecteur audio Android (AudioTrack)
                // Piper génère typiquement du PCM 16-bit mono à 22050 Hz
                val sampleRate = 22050
                val channelConfig = AudioFormat.CHANNEL_OUT_MONO
                val audioFormat = AudioFormat.ENCODING_PCM_16BIT

                val minBufferSize = AudioTrack.getMinBufferSize(sampleRate, channelConfig, audioFormat)
                
                val audioTrack = AudioTrack.Builder()
                    .setAudioAttributes(
                        AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_MEDIA)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                            .build()
                    )
                    .setAudioFormat(
                        AudioFormat.Builder()
                            .setEncoding(audioFormat)
                            .setSampleRate(sampleRate)
                            .setChannelMask(channelConfig)
                            .build()
                    )
                    .setBufferSizeInBytes(minBufferSize)
                    .setTransferMode(AudioTrack.MODE_STREAM)
                    .build()

                // 3. Lecture du flux
                Log.i(tag, "Orba parle.")
                audioTrack.play()
                audioTrack.write(pcmAudioData, 0, pcmAudioData.size)

                // Attendre la fin de la lecture
                audioTrack.stop()
                audioTrack.release()

            } catch (e: Exception) {
                Log.e(tag, "Erreur lors de la synthèse vocale ou de la lecture", e)
            } catch (e: UnsatisfiedLinkError) {
                Log.e(tag, "NDK non configuré : Impossible d'appeler piper_jni.", e)
            }
        }
    }
}
