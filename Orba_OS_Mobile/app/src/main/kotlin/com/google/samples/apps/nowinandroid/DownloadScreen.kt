package com.google.samples.apps.nowinandroid

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun DownloadScreen(
    downloadState: String,
    progress: Float,
    isGemmaPresent: Boolean,
    isPiperPresent: Boolean,
    onStartDownload: () -> Unit,
    onImportGemma: () -> Unit,
    onImportPiper: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0F0F1A)), // Dark spiritual background
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(32.dp)
        ) {
            Text(
                text = "Éveil d'Orba",
                color = Color.White,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(16.dp))

            if (downloadState == "NEED_DOWNLOAD") {
                Text(
                    text = "L'intelligence d'Orba nécessite le téléchargement des réseaux neuronaux hors-ligne (Gemma et Piper TTS). Poids estimé : 2.5 Go.",
                    color = Color.LightGray,
                    textAlign = TextAlign.Center,
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.height(24.dp))
                Button(
                    onClick = onStartDownload,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF9b4dca)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Télécharger et Initialiser via Internet", color = Color.White)
                }

                Spacer(modifier = Modifier.height(32.dp))
                HorizontalDivider(color = Color.Gray.copy(alpha = 0.3f))
                Spacer(modifier = Modifier.height(24.dp))

                Text(
                    text = "Souveraineté (Import local sans Internet)",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    textAlign = TextAlign.Center
                )
                Spacer(modifier = Modifier.height(16.dp))

                // Gemma model row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Gemma (gemma.bin) : \n" + if (isGemmaPresent) "✅ Présent" else "❌ Manquant",
                        color = if (isGemmaPresent) Color(0xFF81C784) else Color(0xFFE57373),
                        fontSize = 14.sp,
                        modifier = Modifier.weight(1f)
                    )
                    Button(
                        onClick = onImportGemma,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2d3748))
                    ) {
                        Text("Importer", color = Color.White, fontSize = 12.sp)
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Piper voice model row
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Voix (fr_FR-siwis-medium.onnx) : \n" + if (isPiperPresent) "✅ Présent" else "❌ Manquant",
                        color = if (isPiperPresent) Color(0xFF81C784) else Color(0xFFE57373),
                        fontSize = 14.sp,
                        modifier = Modifier.weight(1f)
                    )
                    Button(
                        onClick = onImportPiper,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2d3748))
                    ) {
                        Text("Importer", color = Color.White, fontSize = 12.sp)
                    }
                }

            } else if (downloadState == "DOWNLOADING") {
                Text(
                    text = "Téléchargement en cours...",
                    color = Color.White,
                    fontSize = 18.sp
                )
                Spacer(modifier = Modifier.height(16.dp))
                LinearProgressIndicator(
                    progress = { progress },
                    modifier = Modifier.fillMaxWidth(),
                    color = Color(0xFF9b4dca),
                    trackColor = Color.DarkGray
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "${(progress * 100).toInt()}%",
                    color = Color.LightGray
                )
            }
        }
    }
}
