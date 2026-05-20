import os
import wave
import logging
import asyncio
import numpy as np
import sounddevice as sd

# We'll import piper if available, otherwise fallback to mock/subprocess
try:
    from piper import PiperVoice
except ImportError:
    PiperVoice = None

logger = logging.getLogger("OrbaDesktop.TTS")

class LocalTTS:
    def __init__(self):
        self.model_path = os.environ.get("PIPER_MODEL_PATH", "models/fr_FR-upmc-medium.onnx")
        self.voice = None
        self.output_device = None
        self.sample_rate = 22050 # Piper voices are usually 22050Hz or 16000Hz

    def initialize(self) -> bool:
        """Initialize the Piper engine."""
        if PiperVoice is None:
            logger.warning("Bibliothèque 'piper-tts' non installée. Mode simulation TTS activé.")
            return False

        if not os.path.exists(self.model_path):
            logger.warning(f"Modèle Piper introuvable à {self.model_path}. Mode simulation TTS activé.")
            return False

        try:
            logger.info(f"Chargement du modèle vocal Piper : {self.model_path}...")
            # Load model and config
            config_path = self.model_path + ".json"
            self.voice = PiperVoice.load(self.model_path, config_path)
            self.sample_rate = self.voice.config.sample_rate
            logger.info(f"Modèle vocal Piper chargé (Taux d'échantillonnage : {self.sample_rate}Hz).")
            return True
        except Exception as e:
            logger.error(f"Erreur d'initialisation de Piper Voice : {e}")
            return False

    async def speak(self, text: str, volume_callback):
        """Synthesize and play speech, calculating RMS volume chunks to animate the UI."""
        # 1. Fallback if Piper is not configured
        if not self.voice or PiperVoice is None:
            logger.info(f"[TTS SIMULATION] {text}")
            # Simulate speech duration and volume fluctuations
            await self._simulate_speech_animation(text, volume_callback)
            return

        # 2. Run synthesis in thread pool (since it's CPU intensive and synchronous)
        try:
            logger.info(f"Synthèse vocale locale pour : {text}")
            audio_generator = self.voice.synthesize_stream(text)
            
            # Open sounddevice stream
            # Piper returns int16 raw PCM frames
            loop = asyncio.get_running_loop()
            
            def play_stream():
                with sd.RawOutputStream(
                    samplerate=self.sample_rate,
                    blocksize=1024,
                    dtype='int16',
                    channels=1
                ) as stream:
                    for audio_bytes in audio_generator:
                        # Write audio chunk to output speakers
                        stream.write(audio_bytes)
                        
                        # Calculate RMS volume of the current chunk for visual animation
                        samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
                        if len(samples) > 0:
                            # Normalize sample values
                            normalized = samples / 32768.0
                            rms = np.sqrt(np.mean(normalized ** 2))
                            # Clip between 0 and 1
                            rms_val = float(np.clip(rms * 2.5, 0.0, 1.0))
                            
                            # Push volume metric back to main loop to animate OrbaSphere
                            loop.call_soon_threadsafe(volume_callback, rms_val)

            await asyncio.to_thread(play_stream)
            # Final reset of volume
            volume_callback(0.0)
            
        except Exception as e:
            logger.error(f"Erreur durant la lecture audio Piper : {e}")
            # Simulate as backup
            await self._simulate_speech_animation(text, volume_callback)

    async def _simulate_speech_animation(self, text: str, volume_callback):
        """Fallback simulator that generates rhythmic decibel waves for WebGL sphere animations."""
        words = text.split()
        duration = len(words) * 0.35 # Approx 350ms per word
        steps = int(duration * 20) # 20 ticks per second
        
        for i in range(steps):
            # Sine wave simulation of speech rhythm
            simulated_volume = 0.3 + 0.5 * abs(np.sin(i * 0.6))
            volume_callback(simulated_volume)
            await asyncio.sleep(0.05)
            
        volume_callback(0.0)
