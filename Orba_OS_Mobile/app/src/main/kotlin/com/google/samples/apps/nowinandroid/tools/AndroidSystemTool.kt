package com.google.samples.apps.nowinandroid.tools

import android.content.Context
import android.content.Intent
import android.hardware.camera2.CameraManager
import android.media.AudioManager
import android.os.BatteryManager
import android.provider.AlarmClock
import android.provider.Settings
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AndroidSystemTool @Inject constructor(
    @ApplicationContext private val context: Context
) : OrbaTool {
    override val name = "android_system"
    override val description = "Exécute diverses actions physiques et logicielles sur l'appareil Android."

    override suspend fun execute(params: Map<String, String>): String {
        return withContext(Dispatchers.IO) {
            val action = params["action"] ?: return@withContext "Aucune action spécifiée."
            
            when (action) {
                "battery" -> getBatteryLevel()
                "flashlight_on" -> toggleFlashlight(true)
                "flashlight_off" -> toggleFlashlight(false)
                "get_time" -> getCurrentTime()
                "mute" -> setVolumeMode(AudioManager.RINGER_MODE_SILENT)
                "unmute" -> setVolumeMode(AudioManager.RINGER_MODE_NORMAL)
                "open_youtube" -> openApp("com.google.android.youtube")
                "open_gmail" -> openApp("com.google.android.gm")
                "open_maps" -> openApp("com.google.android.apps.maps")
                "open_camera" -> openApp("android.media.action.IMAGE_CAPTURE")
                "open_settings" -> openSettings(Settings.ACTION_SETTINGS)
                "open_wifi_settings" -> openSettings(Settings.ACTION_WIFI_SETTINGS)
                "open_bluetooth_settings" -> openSettings(Settings.ACTION_BLUETOOTH_SETTINGS)
                "set_alarm" -> setAlarm(params["hours"]?.toIntOrNull() ?: 8, params["minutes"]?.toIntOrNull() ?: 0, params["label"] ?: "Alarme Orba")
                "web_search" -> searchWeb(params["query"] ?: "")
                else -> "L'action '$action' n'est pas reconnue."
            }
        }
    }

    private fun getBatteryLevel(): String {
        return try {
            val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            val batLevel = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            "Le niveau de batterie est à $batLevel%."
        } catch (e: Exception) {
            "Je n'ai pas pu lire le niveau de batterie."
        }
    }

    private fun toggleFlashlight(on: Boolean): String {
        return try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraId = cameraManager.cameraIdList[0]
            cameraManager.setTorchMode(cameraId, on)
            if (on) "La lampe torche est maintenant allumée." else "La lampe torche est éteinte."
        } catch (e: Exception) {
            "Impossible de contrôler la lampe torche. Le flash est peut-être déjà utilisé."
        }
    }

    private fun getCurrentTime(): String {
        return try {
            val sdf = SimpleDateFormat("EEEE d MMMM yyyy 'à' HH'h'mm", Locale.getDefault())
            val currentDate = sdf.format(Date())
            "Nous sommes le $currentDate."
        } catch (e: Exception) {
            "Je n'ai pas pu récupérer l'heure actuelle."
        }
    }

    private fun setVolumeMode(mode: Int): String {
        return try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
            audioManager.ringerMode = mode
            when (mode) {
                AudioManager.RINGER_MODE_SILENT -> "Le téléphone est maintenant en mode silencieux."
                AudioManager.RINGER_MODE_NORMAL -> "Le téléphone est de retour en mode normal."
                else -> "Mode de volume modifié."
            }
        } catch (e: Exception) {
            "Je n'ai pas l'autorisation de modifier le mode de volume. Veuillez vérifier les permissions d'accès 'Ne pas déranger'."
        }
    }

    private fun openApp(packageName: String): String {
        return try {
            if (packageName == "android.media.action.IMAGE_CAPTURE") {
                val intent = Intent(packageName).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                context.startActivity(intent)
                return "Appareil photo lancé."
            }
            val intent = context.packageManager.getLaunchIntentForPackage(packageName)
            if (intent != null) {
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(intent)
                "L'application a été lancée avec succès."
            } else {
                "L'application n'est pas installée sur cet appareil."
            }
        } catch (e: Exception) {
            "Erreur lors du lancement de l'application."
        }
    }

    private fun openSettings(action: String): String {
        return try {
            val intent = Intent(action).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            "Paramètres ouverts."
        } catch (e: Exception) {
            "Impossible d'ouvrir l'écran de paramètres demandé."
        }
    }

    private fun setAlarm(hour: Int, minutes: Int, label: String): String {
        return try {
            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minutes)
                putExtra(AlarmClock.EXTRA_MESSAGE, label)
                putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
            "Alarme réglée pour ${hour}h${if (minutes < 10) "0$minutes" else minutes}."
        } catch (e: Exception) {
            "Impossible de configurer l'alarme."
        }
    }

    private fun searchWeb(query: String): String {
        if (query.isBlank()) return "Recherche vide."
        return try {
            val directIntent = Intent(Intent.ACTION_WEB_SEARCH).apply {
                putExtra("query", query)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(directIntent)
            "Recherche lancée pour : $query"
        } catch (e: Exception) {
            "Impossible de lancer la recherche web."
        }
    }
}
