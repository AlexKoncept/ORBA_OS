package com.google.samples.apps.nowinandroid.core.common.intelligence

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

val Context.dataStore by preferencesDataStore(name = "orba_memory")

@Singleton
class OrbaMemory @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val USER_NAME_KEY = stringPreferencesKey("user_name")
    private val USER_CONTEXT_KEY = stringPreferencesKey("user_context")
    private val SELECTED_VOICE_KEY = stringPreferencesKey("selected_voice")

    val userName: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[USER_NAME_KEY] ?: "Alex Koncept"
    }

    val userContext: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[USER_CONTEXT_KEY] ?: "J'aime la technologie et le design minimaliste."
    }

    val selectedVoice: Flow<String> = context.dataStore.data.map { preferences ->
        preferences[SELECTED_VOICE_KEY] ?: "Kore" // Options: Kore, Puck, Charon, Zephyr, Fenrir
    }

    suspend fun updateProfile(name: String, contextInfo: String, voice: String) {
        context.dataStore.edit { preferences ->
            preferences[USER_NAME_KEY] = name
            preferences[USER_CONTEXT_KEY] = contextInfo
            preferences[SELECTED_VOICE_KEY] = voice
        }
    }

    suspend fun eraseMemory() {
        context.dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
