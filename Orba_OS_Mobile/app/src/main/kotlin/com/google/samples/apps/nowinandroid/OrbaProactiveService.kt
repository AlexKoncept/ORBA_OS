package com.google.samples.apps.nowinandroid

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import com.google.samples.apps.nowinandroid.core.common.audio.OrbaVoice
import com.google.samples.apps.nowinandroid.core.common.intelligence.OrbaBrain
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class OrbaProactiveService : Service() {

    @Inject lateinit var brain: OrbaBrain
    @Inject lateinit var voice: OrbaVoice

    private val serviceJob = Job()
    private val serviceScope = CoroutineScope(Dispatchers.IO + serviceJob)

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(1, createNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.i("OrbaProactive", "Le service proactif d'Orba a démarré en arrière-plan.")
        startProactiveLoop()
        return START_STICKY // Redémarre automatiquement si le système le tue
    }

    private fun startProactiveLoop() {
        serviceScope.launch {
            while (true) {
                // Par exemple, on vérifie un contexte (heure, notifications) toutes les heures.
                // Ici, une boucle factice pour simuler l'agenticité autonome.
                delay(3600000L) // Attend 1 heure

                val timeContext = "Il est temps de faire un point. Génère un message proactif court pour l'utilisateur."
                
                var fullResponse = ""
                brain.think(timeContext).collect { chunk ->
                    fullResponse += chunk
                }

                if (fullResponse.isNotBlank()) {
                    Log.i("OrbaProactive", "Orba prend la parole d'elle-même : \$fullResponse")
                    voice.speak(fullResponse)
                }
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        serviceJob.cancel()
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            "orba_service_channel",
            "Orba Background Service",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Maintient l'intelligence d'Orba active en tâche de fond."
        }
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun createNotification(): Notification {
        return Notification.Builder(this, "orba_service_channel")
            .setContentTitle("Orba OS")
            .setContentText("L'intelligence invisible veille sur vous.")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now) // Remplacer par le logo plus tard
            .build()
    }
}
