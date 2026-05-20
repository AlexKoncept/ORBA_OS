cmake_minimum_required(VERSION 3.22.1)

project("piper_jni")

# Scaffold pour la compilation de Piper TTS
# C'est ici que tu devras lier les sources de piper1-gpl (libpiper) et espeak-ng plus tard.

add_library(
        piper_jni
        SHARED
        piper_jni.cpp)

target_link_libraries(
        piper_jni
        android
        log)
