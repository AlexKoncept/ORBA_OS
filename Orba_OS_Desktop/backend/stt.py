import os
import json
import queue
import logging
import asyncio
import sounddevice as sd
from vosk import Model, KaldiRecognizer

logger = logging.getLogger("OrbaDesktop.STT")

# Thread-safe queue for audio chunks
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Callback from sounddevice to receive audio chunks."""
    if status:
        logger.warning(f"Audio input status: {status}")
    audio_queue.put(bytes(indata))

class LocalSTT:
    def __init__(self, lang: str = "fr"):
        self.lang = lang
        self.model = None
        self.recognizer = None
        self.sample_rate = 16000

    def initialize(self) -> bool:
        """Download and load the Vosk model in a background thread."""
        try:
            logger.info(f"Chargement du modèle de reconnaissance vocale Vosk ({self.lang})...")
            # Vosk auto-downloads the model if lang is specified
            self.model = Model(lang=self.lang)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            logger.info("Modèle Vosk chargé avec succès.")
            return True
        except Exception as e:
            logger.error(f"Impossible d'initialiser Vosk : {e}")
            return False

    async def listen_loop(self, callback_func):
        """Asynchronous microphone listening loop."""
        if not self.model:
            if not self.initialize():
                logger.error("Arrêt de la boucle STT : modèle non initialisé.")
                return

        # Start sounddevice input stream
        # 16000Hz mono is standard for speech recognition engines
        stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=audio_callback
        )

        logger.info("Microphone activé. Écoute en cours...")
        with stream:
            while True:
                # Run the blocking queue.get in an executor thread
                try:
                    data = await asyncio.to_thread(audio_queue.get, timeout=0.1)
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue

                # Run recognizer in a thread pool to avoid blocking FastAPI event loop
                if self.recognizer.AcceptWaveform(data):
                    res = json.loads(self.recognizer.Result())
                    text = res.get("text", "").strip()
                    if text:
                        logger.info(f"Transcription finale : {text}")
                        # Trigger the callback with recognized text
                        asyncio.create_task(callback_func(text))
                else:
                    # Partial speech result (visualizer could use this if needed)
                    pass
