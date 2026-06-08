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

package ru.nti.sbor.auth

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import ru.nti.sbor.config.ApiConfig
import ru.nti.sbor.data.repository.LaborRepository
import ru.nti.sbor.data.settings.SecureServerSettings
import ru.nti.sbor.domain.model.WorkerProfile
import ru.nti.sbor.sync.NtiHttpClient
import ru.nti.sbor.sync.dto.LoginRequest
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

sealed class AuthResult {
    data class Success(val displayName: String) : AuthResult()
    data class Error(val message: String) : AuthResult()
}

/** Авторизация: только логин/пароль, URL API из сборки. */
class AuthRepository(
    private val secureSettings: SecureServerSettings,
    private val laborRepository: LaborRepository,
) {
    private val _loggedIn = MutableStateFlow(secureSettings.isLoggedIn())
    val loggedIn: StateFlow<Boolean> = _loggedIn.asStateFlow()

    init {
        secureSettings.ensureServerUrl(ApiConfig.baseUrl)
    }

    fun refreshAuthState() {
        _loggedIn.value = secureSettings.isLoggedIn()
    }

    suspend fun login(username: String, password: String): AuthResult = withContext(Dispatchers.IO) {
        if (username.isBlank() || password.isBlank()) {
            return@withContext AuthResult.Error("Введите логин и пароль")
        }
        val baseUrl = ApiConfig.baseUrl
        try {
            val response = NtiHttpClient(baseUrl).login(
                LoginRequest(username = username.trim(), password = password),
            )
            secureSettings.saveSession(
                serverUrl = baseUrl,
                accessToken = response.accessToken,
                username = username.trim().lowercase(),
                displayName = response.displayName,
            )
            if (response.displayName.isNotBlank()) {
                laborRepository.saveProfile(
                    WorkerProfile(
                        worker = response.displayName,
                        tabNumber = response.tabNumber,
                    ),
                )
            }
            _loggedIn.value = true
            AuthResult.Success(response.displayName)
        } catch (e: Exception) {
            AuthResult.Error(mapConnectionError(e, baseUrl))
        }
    }

    suspend fun logout(): Unit = withContext(Dispatchers.IO) {
        val auth = secureSettings.bearerHeader()
        val url = secureSettings.getServerUrl().ifBlank { ApiConfig.baseUrl }
        if (auth != null) {
            try {
                NtiHttpClient(url).logout(auth)
            } catch (_: Exception) {
            }
        }
        secureSettings.clearSession()
        _loggedIn.value = false
    }

    private fun mapConnectionError(e: Exception, baseUrl: String): String {
        when (e) {
            is SocketTimeoutException ->
                return "Таймаут подключения к $baseUrl. Телефон и ПК должны быть в одной Wi‑Fi, сервер запущен (./scripts/run_dev.sh)."
            is ConnectException, is UnknownHostException ->
                return "Сервер недоступен ($baseUrl). Запустите backend на ПК и пересоберите APK с IP: ./scripts/detect_api_url.sh"
        }
        val msg = e.message.orEmpty()
        if (msg.contains("timeout", ignoreCase = true)) {
            return "Таймаут ($baseUrl). Проверьте Wi‑Fi и адрес API в сборке приложения."
        }
        return msg.ifBlank { "Ошибка входа" }
    }

    suspend fun validateSession(): Boolean = withContext(Dispatchers.IO) {
        val auth = secureSettings.bearerHeader() ?: return@withContext false
        val url = secureSettings.getServerUrl().ifBlank { ApiConfig.baseUrl }
        return@withContext try {
            NtiHttpClient(url).currentUser(auth)
            true
        } catch (_: Exception) {
            secureSettings.clearSession()
            _loggedIn.value = false
            false
        }
    }
}
