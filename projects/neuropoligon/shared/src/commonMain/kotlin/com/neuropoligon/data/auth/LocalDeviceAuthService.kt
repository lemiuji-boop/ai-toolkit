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

import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.auth.AuthState
import com.neuropoligon.domain.auth.AuthUser
import com.neuropoligon.platform.SecureStorage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlin.random.Random
import kotlinx.datetime.Clock
import kotlinx.datetime.DateTimeUnit
import kotlinx.datetime.TimeZone
import kotlinx.datetime.plus

/**
 * Локальная авторизация на устройстве, если backend недоступен.
 * Код подтверждения показывается в UI (не по SMTP).
 */
public class LocalDeviceAuthService(
    private val secureStorage: SecureStorage,
) : AuthService {
    private val json = Json { ignoreUnknownKeys = true }
    private val state = MutableStateFlow<AuthState>(AuthState.Guest)
    private val _lastVerificationCode = MutableStateFlow<String?>(null)
    public val lastVerificationCode: Flow<String?> = _lastVerificationCode.asStateFlow()

    override val currentUser: Flow<AuthState> = state.asStateFlow()

    override fun isConfigured(): Boolean = true

    override suspend fun signUpWithEmail(email: String, password: String): Result<Unit> {
        if (email.isBlank() || password.length < 6) {
            return Result.failure(IllegalArgumentException("Почта и пароль (мин. 6 символов) обязательны."))
        }
        val normalized = email.trim().lowercase()
        val users = loadUsers().toMutableMap()
        val code = randomCode()
        users[normalized] = LocalAuthRecord(
            email = normalized,
            password = password,
            verified = false,
            verifyCode = code,
            verifyExpiresEpochMs = expiresIn30Min(),
        )
        saveUsers(users)
        _lastVerificationCode.value = code
        state.value = AuthState.PendingVerification(normalized)
        return Result.success(Unit)
    }

    override suspend fun signInWithEmail(email: String, password: String): Result<Unit> {
        val normalized = email.trim().lowercase()
        val user = loadUsers()[normalized]
            ?: return Result.failure(IllegalArgumentException("Аккаунт не найден. Сначала зарегистрируйтесь."))
        if (user.password != password) {
            return Result.failure(IllegalArgumentException("Неверная почта или пароль."))
        }
        if (!user.verified) {
            state.value = AuthState.PendingVerification(normalized)
            _lastVerificationCode.value = user.verifyCode
            return Result.failure(IllegalArgumentException("Подтвердите почту кодом из приложения."))
        }
        saveSession(normalized)
        return Result.success(Unit)
    }

    override suspend fun sendMagicLink(email: String): Result<Unit> = resendCode(email)

    public suspend fun resendCode(email: String): Result<Unit> {
        val normalized = email.trim().lowercase()
        val users = loadUsers().toMutableMap()
        val user = users[normalized]
            ?: return Result.failure(IllegalArgumentException("Сначала зарегистрируйтесь."))
        val code = randomCode()
        users[normalized] = user.copy(
            verifyCode = code,
            verifyExpiresEpochMs = expiresIn30Min(),
        )
        saveUsers(users)
        _lastVerificationCode.value = code
        return Result.success(Unit)
    }

    override suspend fun verifyOtp(email: String, token: String): Result<Unit> {
        val normalized = email.trim().lowercase()
        val users = loadUsers().toMutableMap()
        val user = users[normalized]
            ?: return Result.failure(IllegalArgumentException("Пользователь не найден."))
        if (user.verifyCode != token.trim()) {
            return Result.failure(IllegalArgumentException("Неверный код."))
        }
        if (Clock.System.now().toEpochMilliseconds() > user.verifyExpiresEpochMs) {
            return Result.failure(IllegalArgumentException("Код истёк. Запросите новый."))
        }
        users[normalized] = user.copy(verified = true, verifyCode = null)
        saveUsers(users)
        _lastVerificationCode.value = null
        saveSession(normalized)
        return Result.success(Unit)
    }

    override suspend fun signOut() {
        secureStorage.remove(KEY_SESSION_EMAIL)
        state.value = AuthState.Guest
    }

    public suspend fun restoreSessionIfNeeded() {
        val email = secureStorage.get(KEY_SESSION_EMAIL) ?: return
        if (loadUsers()[email]?.verified == true) {
            state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
        }
    }

    private suspend fun saveSession(email: String) {
        secureStorage.set(KEY_SESSION_EMAIL, email)
        state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
    }

    private suspend fun loadUsers(): Map<String, LocalAuthRecord> {
        val raw = secureStorage.get(KEY_USERS) ?: return emptyMap()
        return runCatching {
            json.decodeFromString<Map<String, LocalAuthRecord>>(raw)
        }.getOrDefault(emptyMap())
    }

    private suspend fun saveUsers(users: Map<String, LocalAuthRecord>) {
        secureStorage.set(KEY_USERS, json.encodeToString(users))
    }

    private fun randomCode(): String = (100_000 + Random.nextInt(900_000)).toString()

    private fun expiresIn30Min(): Long =
        Clock.System.now().plus(30, DateTimeUnit.MINUTE, TimeZone.currentSystemDefault())
            .toEpochMilliseconds()

    public fun peekState(): AuthState = state.value

    @Serializable
    private data class LocalAuthRecord(
        val email: String,
        val password: String,
        val verified: Boolean,
        val verifyCode: String? = null,
        val verifyExpiresEpochMs: Long = 0L,
    )

    private companion object {
        private const val KEY_USERS = "local_auth_users"
        private const val KEY_SESSION_EMAIL = "local_auth_session_email"
    }
}
