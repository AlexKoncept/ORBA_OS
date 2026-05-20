#include <jni.h>
#include <string>
#include <vector>
#include <mutex>
#include <android/log.h>

// On part du principe que piper.hpp et les dépendances (onnxruntime, piper-phonemize)
// sont gérées par votre CMakeLists.txt (dossier piper1-gpl).
#include <piper.hpp>

#define LOG_TAG "PiperJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// Variables globales pour conserver le modèle ONNX chargé en RAM entre les phrases (crucial pour le temps réel)
static piper::PiperConfig piperConfig;
static piper::Voice piperVoice;
static std::string currentModelPath = "";
static std::mutex piperMutex;
static bool isVoiceLoaded = false;

extern "C" JNIEXPORT jbyteArray JNICALL
Java_com_google_samples_apps_nowinandroid_core_common_audio_OrbaVoice_synthesizeText(
        JNIEnv* env,
        jobject thiz,
        jstring text,
        jstring modelPath) {
    
    const char *nativeText = env->GetStringUTFChars(text, nullptr);
    const char *nativeModelPath = env->GetStringUTFChars(modelPath, nullptr);
    
    std::string textStr(nativeText);
    std::string modelPathStr(nativeModelPath);
    
    env->ReleaseStringUTFChars(text, nativeText);
    env->ReleaseStringUTFChars(modelPath, nativeModelPath);
    
    // Verrouillage du thread pour éviter les conflits mémoires si Orba parle plusieurs fois très vite
    std::lock_guard<std::mutex> lock(piperMutex);
    
    // 1. Chargement Conditionnel du Modèle Vocal (Cold Start)
    if (!isVoiceLoaded || currentModelPath != modelPathStr) {
        LOGI("Chargement du modele vocal Piper (ONNX) : %s", modelPathStr.c_str());
        
        // La convention de Piper exige que le config json soit au même endroit avec l'extension ".json"
        std::string configPath = modelPathStr + ".json";
        std::optional<piper::SpeakerId> speakerId;
        
        try {
            piper::loadVoice(piperConfig, modelPathStr, configPath, piperVoice, speakerId);
            currentModelPath = modelPathStr;
            isVoiceLoaded = true;
            LOGI("Modèle vocal chargé avec succès en RAM (NPU/CPU) !");
        } catch (const std::exception& e) {
            LOGE("Erreur fatale lors du chargement de la voix Piper : %s", e.what());
            return env->NewByteArray(0);
        }
    }
    
    // 2. Synthèse Vocale -> Audio PCM (16-bit Mono)
    LOGI("Synthèse vocale en cours : '%s'", textStr.c_str());
    
    std::vector<int16_t> audioBuffer;
    piper::SynthesisResult result;
    
    try {
        // Exécution de l'inférence. L'audio PCM brut s'accumule automatiquement dans audioBuffer.
        piper::textToAudio(piperConfig, piperVoice, textStr, audioBuffer, result, nullptr);
        LOGI("Synthèse terminée ! %zu samples audio générés en %f secondes.", audioBuffer.size(), result.inferSeconds);
    } catch (const std::exception& e) {
        LOGE("Erreur interne ONNX durant la synthèse vocale : %s", e.what());
    }
    
    // 3. Conversion C++ std::vector -> Java jbyteArray pour l'AudioTrack d'Android
    size_t byteSize = audioBuffer.size() * sizeof(int16_t);
    jbyteArray jAudioArray = env->NewByteArray(byteSize);
    
    if (byteSize > 0) {
        env->SetByteArrayRegion(jAudioArray, 0, byteSize, reinterpret_cast<const jbyte*>(audioBuffer.data()));
    }
    
    return jAudioArray;
}
