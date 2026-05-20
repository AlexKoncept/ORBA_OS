package com.google.samples.apps.nowinandroid

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import android.net.Uri
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.google.samples.apps.nowinandroid.core.designsystem.theme.NiaTheme
import com.google.samples.apps.nowinandroid.core.ui.OrbaSphere
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val viewModel: OrbaViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)

        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(
                android.graphics.Color.TRANSPARENT,
            ),
            navigationBarStyle = SystemBarStyle.dark(
                android.graphics.Color.TRANSPARENT,
            ),
        )

        setContent {
            val downloadState by viewModel.downloadState.collectAsStateWithLifecycle()
            val downloadProgress by viewModel.downloadProgress.collectAsStateWithLifecycle()

            val orbaState by viewModel.uiState.collectAsStateWithLifecycle()
            val orbaVolume by viewModel.volume.collectAsStateWithLifecycle()

            val userName by viewModel.userName.collectAsStateWithLifecycle(initialValue = "")
            val userContext by viewModel.userContext.collectAsStateWithLifecycle(initialValue = "")
            val selectedVoice by viewModel.selectedVoice.collectAsStateWithLifecycle(initialValue = "Kore")

            var showProfile by remember { mutableStateOf(false) }

            val gemmaPickerLauncher = rememberLauncherForActivityResult(
                contract = ActivityResultContracts.GetContent()
            ) { uri: Uri? ->
                uri?.let {
                    viewModel.importModel(it, "gemma.bin")
                }
            }

            val piperPickerLauncher = rememberLauncherForActivityResult(
                contract = ActivityResultContracts.GetContent()
            ) { uri: Uri? ->
                uri?.let {
                    viewModel.importModel(it, "fr_FR-siwis-medium.onnx")
                }
            }

            LaunchedEffect(Unit) {
                viewModel.checkModels()
            }

            NiaTheme(
                darkTheme = true,
                androidTheme = false,
                disableDynamicTheming = true,
            ) {
                if (downloadState != "READY") {
                    DownloadScreen(
                        downloadState = downloadState,
                        progress = downloadProgress,
                        isGemmaPresent = viewModel.isGemmaPresent(),
                        isPiperPresent = viewModel.isPiperPresent(),
                        onStartDownload = {
                            viewModel.startModelDownload()
                        },
                        onImportGemma = {
                            gemmaPickerLauncher.launch("*/*")
                        },
                        onImportPiper = {
                            piperPickerLauncher.launch("*/*")
                        }
                    )
                } else {
                    Box(
                        modifier = Modifier.fillMaxSize()
                    ) {
                        // Rend le shader 3D de l'Orbe réactif au ViewModel
                        OrbaSphere(
                            modifier = Modifier
                                .fillMaxSize()
                                .clickable {
                                    if (!showProfile) viewModel.startListening()
                                },
                            state = orbaState,
                            volume = orbaVolume 
                        )

                        // Bouton des paramètres (minimaliste) en haut à droite
                        IconButton(
                            onClick = { showProfile = true },
                            modifier = Modifier
                                .align(Alignment.TopEnd)
                                .padding(top = 48.dp, end = 16.dp) // Pour éviter le status bar
                        ) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Profil",
                                tint = Color.White.copy(alpha = 0.5f) // Discret
                            )
                        }

                        // Affiche l'écran de profil par dessus l'orbe si activé
                        if (showProfile) {
                            ProfileScreen(
                                currentName = userName,
                                currentContext = userContext,
                                currentVoice = selectedVoice,
                                onSaveProfile = { name, ctx, voice ->
                                    viewModel.saveProfile(name, ctx, voice)
                                },
                                onDismiss = { showProfile = false }
                            )
                        }
                    }
                }
            }
        }
    }
}
