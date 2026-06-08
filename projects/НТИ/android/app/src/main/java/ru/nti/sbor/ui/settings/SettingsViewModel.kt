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

package ru.nti.sbor.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import ru.nti.sbor.AppContainer
import ru.nti.sbor.data.settings.ThemeMode

data class SettingsUiState(
    val themeMode: ThemeMode = ThemeMode.DARK,
    val fontScale: Float = 1f,
    val highContrast: Boolean = false,
    val largeTouchTargets: Boolean = false,
    val message: String? = null,
    // Поля для устаревших демо-экранов (v4/standard), не используются в prod
    val worker: String = "",
    val tabNumber: String = "",
    val serverUrl: String = "",
    val serverToken: String = "",
    val accountDisplayName: String = "",
    val isLoggedIn: Boolean = false,
    val isBusy: Boolean = false,
    val confirmClear: Boolean = false,
)

class SettingsViewModel(private val container: AppContainer) : ViewModel() {
    private val _state = MutableStateFlow(SettingsUiState())
    val state: StateFlow<SettingsUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            container.appPreferences.accessibility.collect { prefs ->
                _state.update {
                    it.copy(
                        themeMode = prefs.themeMode,
                        fontScale = prefs.fontScale,
                        highContrast = prefs.highContrast,
                        largeTouchTargets = prefs.largeTouchTargets,
                    )
                }
            }
        }
    }

    fun setTheme(mode: ThemeMode) {
        viewModelScope.launch {
            container.appPreferences.setThemeMode(mode)
            _state.update { it.copy(themeMode = mode, message = "Сохранено") }
        }
    }

    fun setFontScale(scale: Float) {
        viewModelScope.launch {
            container.appPreferences.setFontScale(scale)
            _state.update { it.copy(fontScale = scale, message = "Размер шрифта сохранён") }
        }
    }

    fun setHighContrast(enabled: Boolean) {
        viewModelScope.launch {
            container.appPreferences.setHighContrast(enabled)
            _state.update { it.copy(highContrast = enabled) }
        }
    }

    fun setLargeTouch(enabled: Boolean) {
        viewModelScope.launch {
            container.appPreferences.setLargeTouchTargets(enabled)
            _state.update { it.copy(largeTouchTargets = enabled) }
        }
    }
}

class SettingsViewModelFactory(private val container: AppContainer) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(SettingsViewModel::class.java)) {
            return SettingsViewModel(container) as T
        }
        throw IllegalArgumentException("Unknown ViewModel")
    }
}
