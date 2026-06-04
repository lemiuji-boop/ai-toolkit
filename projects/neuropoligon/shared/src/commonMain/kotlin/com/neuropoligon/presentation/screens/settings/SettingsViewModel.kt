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

package com.neuropoligon.presentation.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.data.auth.HybridAuthService
import com.neuropoligon.domain.ai.AiProvider
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.domain.settings.SettingsRepository
import com.neuropoligon.platform.SecureStorage
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public class SettingsViewModel(
    private val settingsRepository: SettingsRepository,
    private val secureStorage: SecureStorage,
    progressRepository: com.neuropoligon.domain.progress.ProgressRepository,
    authService: AuthService,
) : ViewModel() {
    private val hybrid = authService as? HybridAuthService

    private val _level = MutableStateFlow(DifficultyLevel.Zero)
    public val level: StateFlow<DifficultyLevel> = _level.asStateFlow()
    private val _apiKey = MutableStateFlow("")
    public val apiKey: StateFlow<String> = _apiKey.asStateFlow()
    private val _provider = MutableStateFlow(AiProvider.OpenAI)
    public val provider: StateFlow<AiProvider> = _provider.asStateFlow()
    private val _saveMessage = MutableStateFlow<String?>(null)
    public val saveMessage: StateFlow<String?> = _saveMessage.asStateFlow()
    private val _authServerUrl = MutableStateFlow("")
    public val authServerUrl: StateFlow<String> = _authServerUrl.asStateFlow()
    public val webWarning: Boolean = com.neuropoligon.platform.isWebPlatform()
    public val completedCount: StateFlow<Int> = progressRepository.observeCompleted().map { it.map { row -> row.moduleId }.distinct().size }.stateIn(viewModelScope, kotlinx.coroutines.flow.SharingStarted.WhileSubscribed(5_000), 0)
    public val repetitionCount: StateFlow<Int> = progressRepository.observeCards().map { it.size }.stateIn(viewModelScope, kotlinx.coroutines.flow.SharingStarted.WhileSubscribed(5_000), 0)
    public val noteCount: StateFlow<Int> = progressRepository.observeNotes().map { it.count { note -> note.noteId.startsWith("note-") && note.text.isNotBlank() } }.stateIn(viewModelScope, kotlinx.coroutines.flow.SharingStarted.WhileSubscribed(5_000), 0)
    public val bookmarkCount: StateFlow<Int> = progressRepository.observeNotes().map { it.count { note -> note.noteId.startsWith("bookmark-") } }.stateIn(viewModelScope, kotlinx.coroutines.flow.SharingStarted.WhileSubscribed(5_000), 0)

    init {
        viewModelScope.launch {
            _level.value = settingsRepository.getDifficultyLevel()
            loadApiKeyForProvider(_provider.value)
            _authServerUrl.value = hybrid?.getApiBaseUrl().orEmpty()
        }
    }

    public fun setLevel(level: DifficultyLevel) {
        viewModelScope.launch {
            settingsRepository.setDifficultyLevel(level)
            _level.value = level
        }
    }

    public fun saveApiKey() {
        val trimmed = _apiKey.value.trim()
        if (trimmed.isEmpty()) {
            _saveMessage.value = "Введите ключ — поле пустое."
            return
        }
        viewModelScope.launch {
            secureStorage.set(apiKeyStorageKey(_provider.value), trimmed)
            _saveMessage.value = "Ключ ${providerLabel(_provider.value)} сохранён."
        }
    }

    public fun updateApiKey(value: String) {
        _apiKey.value = value
        _saveMessage.value = null
    }

    public fun updateProvider(provider: AiProvider) {
        _provider.value = provider
        viewModelScope.launch { loadApiKeyForProvider(provider) }
    }

    public fun updateAuthServerUrl(value: String) {
        _authServerUrl.value = value
    }

    public fun saveAuthServerUrl() {
        viewModelScope.launch {
            hybrid?.setApiBaseUrl(_authServerUrl.value)
            _saveMessage.value = "URL сервера авторизации сохранён"
        }
    }

    private suspend fun loadApiKeyForProvider(provider: AiProvider) {
        _apiKey.value = secureStorage.get(apiKeyStorageKey(provider)).orEmpty()
        _saveMessage.value = if (_apiKey.value.isEmpty()) {
            "Ключ для ${providerLabel(provider)} ещё не сохранён."
        } else {
            "Загружен ключ для ${providerLabel(provider)}."
        }
    }

    private fun apiKeyStorageKey(provider: AiProvider): String = "api_key_${provider.name}"

    private fun providerLabel(provider: AiProvider): String = when (provider) {
        AiProvider.OpenAI -> "OpenAI"
        AiProvider.Anthropic -> "Anthropic"
        AiProvider.Gemini -> "Gemini"
        AiProvider.DeepSeek -> "DeepSeek"
        AiProvider.Groq -> "Groq"
        AiProvider.Mistral -> "Mistral"
        AiProvider.Local -> "Local"
    }
}
