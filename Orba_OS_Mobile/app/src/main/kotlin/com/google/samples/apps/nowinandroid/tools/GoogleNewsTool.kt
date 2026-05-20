package com.google.samples.apps.nowinandroid.tools

import android.util.Log
import io.ktor.client.HttpClient
import io.ktor.client.engine.android.Android
import io.ktor.client.request.get
import io.ktor.client.statement.bodyAsText
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import javax.inject.Inject
import javax.inject.Singleton

interface OrbaTool {
    val name: String
    val description: String
    suspend fun execute(params: Map<String, String>): String
}

@Singleton
class GoogleNewsTool @Inject constructor() : OrbaTool {
    override val name = "google_news"
    override val description = "Permet à Orba de récupérer les dernières actualités Google News. Aucun paramètre requis."

    private val client = HttpClient(Android)

    override suspend fun execute(params: Map<String, String>): String {
        return withContext(Dispatchers.IO) {
            try {
                Log.i("GoogleNewsTool", "Recherche des actualités en cours...")
                // Fetching the French Google News RSS feed
                val response = client.get("https://news.google.com/rss?hl=fr&gl=FR&ceid=FR:fr")
                val xmlBody = response.bodyAsText()

                // Very basic XML parsing to extract the top 3 <title> tags
                val titles = extractTitlesFromRss(xmlBody, limit = 3)
                
                if (titles.isEmpty()) {
                    return@withContext "Je n'ai pas pu récupérer les actualités pour le moment."
                }

                val newsText = "Voici les dernières actualités : \n" + titles.joinToString("\n- ", "- ")
                Log.i("GoogleNewsTool", "Actualités récupérées : $newsText")
                newsText
            } catch (e: Exception) {
                Log.e("GoogleNewsTool", "Erreur réseau", e)
                "Erreur lors de la récupération des actualités."
            }
        }
    }

    private fun extractTitlesFromRss(xml: String, limit: Int): List<String> {
        val titles = mutableListOf<String>()
        val titleRegex = "<title>(.*?)</title>".toRegex()
        val matches = titleRegex.findAll(xml)
        
        var count = 0
        for (match in matches) {
            val title = match.groupValues[1]
            // Skip the main channel title usually "Google Actualités"
            if (!title.contains("Google Actualités", ignoreCase = true)) {
                titles.add(title)
                count++
            }
            if (count >= limit) break
        }
        return titles
    }
}
