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

package com.neuropoligon.data.auth

import com.neuropoligon.domain.auth.AUTH_API_BASE_URL_KEY
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.auth.AuthState
import com.neuropoligon.domain.auth.AuthUser
import com.neuropoligon.domain.auth.DEFAULT_AUTH_API_BASE_URL
import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.platform.SecureStorage
import io.ktor.client.plugins.ClientRequestException
import io.ktor.client.plugins.ServerResponseException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Авторизация через backend: регистрация, письмо с кодом, подтверждение, вход.
 * Админ-аккаунты с сервера на Android отклоняются.
 */
public class BackendEmailAuthService(
    private val httpClient: io.ktor.client.HttpClient,
    private val secureStorage: SecureStorage,
    @Suppress("UnusedPrivateProperty")
    private val progressRepository: ProgressRepository,
) : AuthService {
    private val state = MutableStateFlow<AuthState>(AuthState.Guest)

    override val currentUser: Flow<AuthState> = state.asStateFlow()

    public suspend fun restoreSessionIfNeeded() {
        restoreSession()
    }

    override fun isConfigured(): Boolean = true

    override suspend fun signUpWithEmail(email: String, password: String): Result<Unit> {
        if (email.isBlank() || password.length < 6) {
            return Result.failure(IllegalArgumentException("Почта и пароль (мин. 6 символов) обязательны."))
        }
        return runCatching {
            api().register(email.trim().lowercase(), password)
            state.value = AuthState.PendingVerification(email.trim().lowercase())
        }.normalize()
    }

    override suspend fun signInWithEmail(email: String, password: String): Result<Unit> {
        if (email.isBlank() || password.isBlank()) {
            return Result.failure(IllegalArgumentException("Введите почту и пароль."))
        }
        return runCatching {
            val response = api().login(email.trim().lowercase(), password)
            rejectAdminOnMobile(response.role)
            saveSession(response.token, response.email)
        }.normalize()
    }

    override suspend fun sendMagicLink(email: String): Result<Unit> =
        resendVerification(email)

    public suspend fun resendVerification(email: String): Result<Unit> {
        if (email.isBlank()) return Result.failure(IllegalArgumentException("Укажите почту."))
        return runCatching {
            api().resend(email.trim().lowercase())
            Unit
        }.normalize()
    }

    override suspend fun verifyOtp(email: String, token: String): Result<Unit> {
        if (email.isBlank() || token.length < 4) {
            return Result.failure(IllegalArgumentException("Введите почту и код из письма."))
        }
        return runCatching {
            val response = api().verify(email.trim().lowercase(), token.trim())
            rejectAdminOnMobile(response.role)
            saveSession(response.token, response.email)
        }.normalize()
    }

    override suspend fun signOut() {
        secureStorage.remove(KEY_TOKEN)
        secureStorage.remove(KEY_EMAIL)
        state.value = AuthState.Guest
    }

    public suspend fun setApiBaseUrl(url: String) {
        secureStorage.set(AUTH_API_BASE_URL_KEY, url.trim().trimEnd('/'))
    }

    public suspend fun getApiBaseUrl(): String = resolveBaseUrl()

    public suspend fun ping(): Result<String> = runCatching {
        api().health()
        "Сервер доступен"
    }.normalize()

    public fun peekState(): AuthState = state.value

    private suspend fun saveSession(token: String, email: String) {
        secureStorage.set(KEY_TOKEN, token)
        secureStorage.set(KEY_EMAIL, email)
        state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
    }

    private suspend fun restoreSession() {
        val email = secureStorage.get(KEY_EMAIL) ?: return
        val token = secureStorage.get(KEY_TOKEN) ?: return
        if (email.isBlank() || token.isBlank()) return
        state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
    }

    private fun rejectAdminOnMobile(role: String) {
        if (role.equals("admin", ignoreCase = true)) {
            throw IllegalStateException(
                "Вход администратора доступен только через веб-панель, не из приложения.",
            )
        }
    }

    private suspend fun api(): EmailAuthApi = EmailAuthApi(httpClient, resolveBaseUrl())

    private suspend fun resolveBaseUrl(): String =
        secureStorage.get(AUTH_API_BASE_URL_KEY)?.trim()?.trimEnd('/')
            ?.takeIf { it.isNotBlank() }
            ?: DEFAULT_AUTH_API_BASE_URL

    private fun <T> Result<T>.normalize(): Result<T> = fold(
        onSuccess = { Result.success(it) },
        onFailure = { Result.failure(IllegalStateException(mapException(it))) },
    )

    private fun mapException(e: Throwable): String = when (e) {
        is IllegalStateException -> e.message ?: "Ошибка авторизации"
        is ClientRequestException -> "Сервер: ${e.response.status.description}"
        is ServerResponseException -> "Сервер недоступен. Проверьте URL backend и SMTP."
        else -> e.message ?: "Не удалось связаться с сервером авторизации"
    }

    private companion object {
        private const val KEY_TOKEN = "auth_jwt"
        private const val KEY_EMAIL = "auth_email"
    }
}
