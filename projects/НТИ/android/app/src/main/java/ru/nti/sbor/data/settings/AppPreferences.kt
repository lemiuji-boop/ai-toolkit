// Copyright 2026 Rinat Ishmaev
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package ru.nti.sbor.data.settings

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.floatPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("app_prefs")

enum class ThemeMode { LIGHT, DARK, SYSTEM }

/** Настройки отображения для слабовидящих и удобства интерфейса. */
data class AccessibilityPrefs(
    val themeMode: ThemeMode = ThemeMode.DARK,
    val fontScale: Float = 1f,
    val highContrast: Boolean = false,
    val largeTouchTargets: Boolean = false,
)

class AppPreferences(private val context: Context) {
    private val themeKey = stringPreferencesKey("theme_mode")
    private val fontScaleKey = floatPreferencesKey("font_scale")
    private val highContrastKey = booleanPreferencesKey("high_contrast")
    private val largeTouchKey = booleanPreferencesKey("large_touch")

    val themeMode: Flow<ThemeMode> = context.dataStore.data.map { prefs ->
        when (prefs[themeKey]) {
            "LIGHT" -> ThemeMode.LIGHT
            "DARK" -> ThemeMode.DARK
            else -> ThemeMode.SYSTEM
        }
    }

    val accessibility: Flow<AccessibilityPrefs> = context.dataStore.data.map { prefs ->
        AccessibilityPrefs(
            themeMode = when (prefs[themeKey]) {
                "LIGHT" -> ThemeMode.LIGHT
                "DARK" -> ThemeMode.DARK
                else -> ThemeMode.SYSTEM
            },
            fontScale = prefs[fontScaleKey] ?: 1f,
            highContrast = prefs[highContrastKey] ?: false,
            largeTouchTargets = prefs[largeTouchKey] ?: false,
        )
    }

    suspend fun setThemeMode(mode: ThemeMode) {
        context.dataStore.edit { it[themeKey] = mode.name }
    }

    suspend fun setFontScale(scale: Float) {
        context.dataStore.edit { it[fontScaleKey] = scale }
    }

    suspend fun setHighContrast(enabled: Boolean) {
        context.dataStore.edit { it[highContrastKey] = enabled }
    }

    suspend fun setLargeTouchTargets(enabled: Boolean) {
        context.dataStore.edit { it[largeTouchKey] = enabled }
    }
}
