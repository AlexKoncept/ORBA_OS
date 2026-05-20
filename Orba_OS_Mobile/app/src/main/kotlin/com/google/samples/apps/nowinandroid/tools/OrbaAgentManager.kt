package com.google.samples.apps.nowinandroid.tools

import javax.inject.Inject
import javax.inject.Singleton

/**
 * ORBA AGENTS & ORBA FLOW
 * Moteur de décision local ultra-rapide. Il analyse la requête de l'utilisateur
 * et détermine si une action système ou une recherche externe est nécessaire avant de passer la parole au LLM.
 */
@Singleton
class OrbaAgentManager @Inject constructor(
    private val newsTool: GoogleNewsTool,
    private val systemTool: AndroidSystemTool    private val tools = listOf(newsTool, systemTool)

    // Synonym groups for flexible intent routing
    private val triggersOn = listOf("allume", "allumer", "active", "activer", "lance", "lancer", "démarre", "démarrer", "allumée", "allumé")
    private val triggersOff = listOf("éteins", "éteindre", "coupe", "couper", "désactive", "désactiver", "arrête", "arrêter", "éteinte", "éteint")
    private val triggersOpen = listOf("ouvre", "ouvrir", "lance", "lancer", "démarre", "démarrer", "affiche", "afficher", "va sur", "aller sur")

    private val targetsTorche = listOf("torche", "lampe", "lumière", "lumiere", "flash", "projecteur", "éclairage", "eclairage")
    private val targetsBattery = listOf("batterie", "charge", "pourcentage", "pile", "énergie", "energie", "autonomie")
    private val targetsTime = listOf("heure", "date", "jour", "calendrier", "time", "clock", "quelles heures", "quel jour", "quelle date")
    private val targetsMute = listOf("silencieux", "mode muet", "coupe le son", "couper le son", "mode vibreur", "vibreur", "sans son", "muet")
    private val targetsUnmute = listOf("remets le son", "remettre le son", "active le son", "activer le son", "mode normal", "rétablir le son", "rétablis le son", "sonnerie")
    private val targetsNews = listOf("actualité", "actualités", "news", "infos", "information", "informations", "nouvelles", "presse")
    private val targetsSearch = listOf("cherche", "recherche", "trouve", "trouver", "rechercher", "google", "web", "internet")

    private fun normalize(text: String): String {
        return java.text.Normalizer.normalize(text, java.text.Normalizer.Form.NFD)
            .replace(Regex("\\p{InCombiningDiacriticalMarks}+"), "")
            .lowercase()
    }

    private fun getTokens(text: String): Set<String> {
        val normalized = normalize(text)
        return normalized.split(Regex("[\\s,.:;?!\'\"()_-]+")).map { it.trim() }.filter { it.isNotEmpty() }.toSet()
    }

    private fun matches(normalizedPrompt: String, tokens: Set<String>, keywords: List<String>): Boolean {
        return keywords.any { kw ->
            val normKw = normalize(kw)
            if (normKw.contains(" ")) {
                normalizedPrompt.contains(normKw)
            } else {
                tokens.contains(normKw)
            }
        }
    }

    /**
     * Analyse le prompt et exécute les outils appropriés en arrière-plan.
     * @return Le contexte généré par l'outil, ou null si aucun outil n'a été déclenché.
     */
    suspend fun evaluateAndExecute(prompt: String): AgentResult? {
        val normalizedPrompt = normalize(prompt)
        val tokens = getTokens(prompt)
        
        // 1. Recherche Actualités (GoogleNewsTool)
        if (matches(normalizedPrompt, tokens, targetsNews)) {
            val result = newsTool.execute(emptyMap())
            return AgentResult(
                toolName = newsTool.name,
                systemContext = "Voici les actualités récentes trouvées par ton agent : \n$result\nRésume-les brièvement."
            )
        }
        
        // 2. Batterie
        if (matches(normalizedPrompt, tokens, targetsBattery)) {
            val result = systemTool.execute(mapOf("action" to "battery"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "L'état de la batterie est : $result. Informe l'utilisateur de cet état."
            )
        }
        
        // 3. Lampe Torche
        if (matches(normalizedPrompt, tokens, triggersOn) && matches(normalizedPrompt, tokens, targetsTorche)) {
            val result = systemTool.execute(mapOf("action" to "flashlight_on"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Action : $result. Confirme à l'utilisateur que la lampe est allumée."
            )
        }
        if (matches(normalizedPrompt, tokens, triggersOff) && matches(normalizedPrompt, tokens, targetsTorche)) {
            val result = systemTool.execute(mapOf("action" to "flashlight_off"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Action : $result. Confirme à l'utilisateur que la lampe est éteinte."
            )
        }

        // 4. Date & Heure
        if (matches(normalizedPrompt, tokens, targetsTime)) {
            val result = systemTool.execute(mapOf("action" to "get_time"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "L'heure actuelle est : $result. Donne cette information à l'utilisateur."
            )
        }

        // 5. Volume (Silencieux / Normal)
        if (matches(normalizedPrompt, tokens, targetsMute)) {
            val result = systemTool.execute(mapOf("action" to "mute"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Confirme à l'utilisateur que le téléphone est muet."
            )
        }
        if (matches(normalizedPrompt, tokens, targetsUnmute)) {
            val result = systemTool.execute(mapOf("action" to "unmute"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Confirme à l'utilisateur que le son est activé."
            )
        }

        // 6. Ouverture d'Applications Spécifiques
        if (matches(normalizedPrompt, tokens, triggersOpen) && tokens.contains("youtube")) {
            val result = systemTool.execute(mapOf("action" to "open_youtube"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Dis à l'utilisateur que YouTube est lancé."
            )
        }
        if (matches(normalizedPrompt, tokens, triggersOpen) && (tokens.contains("gmail") || tokens.contains("mails") || tokens.contains("mail") || tokens.contains("courriel"))) {
            val result = systemTool.execute(mapOf("action" to "open_gmail"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Dis à l'utilisateur que Gmail est ouvert."
            )
        }
        if (matches(normalizedPrompt, tokens, triggersOpen) && (tokens.contains("maps") || tokens.contains("carte") || tokens.contains("plan"))) {
            val result = systemTool.execute(mapOf("action" to "open_maps"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Dis à l'utilisateur que Google Maps est ouvert."
            )
        }
        if (tokens.contains("camera") || matches(normalizedPrompt, tokens, listOf("photo", "appareil photo")) || (matches(normalizedPrompt, tokens, triggersOpen) && tokens.contains("photo"))) {
            val result = systemTool.execute(mapOf("action" to "open_camera"))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Dis à l'utilisateur que l'appareil photo est ouvert."
            )
        }

        // 7. Paramètres Systèmes (WiFi, Bluetooth, Globaux)
        if (tokens.contains("parametre") || tokens.contains("reglage") || tokens.contains("configuration") || tokens.contains("config")) {
            val result = when {
                tokens.contains("wifi") -> systemTool.execute(mapOf("action" to "open_wifi_settings"))
                tokens.contains("bluetooth") -> systemTool.execute(mapOf("action" to "open_bluetooth_settings"))
                else -> systemTool.execute(mapOf("action" to "open_settings"))
            }
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Confirme à l'utilisateur l'ouverture du volet de configuration."
            )
        }

        // 8. Configuration d'une Alarme (avec parsing basique de l'heure)
        if (tokens.contains("alarme") || tokens.contains("reveil") || tokens.contains("reveiller")) {
            val timeRegex = "(\\d+)\\s*h\\s*(\\d+)?".toRegex()
            val match = timeRegex.find(normalizedPrompt)
            val hours = match?.groupValues?.get(1)?.toIntOrNull() ?: 8
            val minutes = match?.groupValues?.get(2)?.toIntOrNull() ?: 0
            
            val result = systemTool.execute(mapOf(
                "action" to "set_alarm",
                "hours" to hours.toString(),
                "minutes" to minutes.toString(),
                "label" to "Alarme programmée par Orba"
            ))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Confirme l'enregistrement de l'alarme."
            )
        }

        // 9. Recherche Web (Recherche Google)
        if (matches(normalizedPrompt, tokens, targetsSearch)) {
            val queryRegex = "(?:cherche|recherche|trouve|trouver|rechercher)\\s+(?:sur internet|sur le web|sur google)?\\s*(.+)".toRegex()
            val match = queryRegex.find(normalizedPrompt)
            val query = match?.groupValues?.get(1) ?: prompt
            
            val result = systemTool.execute(mapOf(
                "action" to "web_search",
                "query" to query
            ))
            return AgentResult(
                toolName = systemTool.name,
                systemContext = "Résultat : $result. Dis à l'utilisateur que la recherche est initiée."
            )
        }

        // Aucun outil déclenché, c'est une conversation normale.
        return null
    }
}

data class AgentResult(
    val toolName: String,
    val systemContext: String
)
