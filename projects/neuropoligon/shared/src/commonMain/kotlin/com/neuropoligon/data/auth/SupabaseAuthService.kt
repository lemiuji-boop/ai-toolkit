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
import com.neuropoligon.domain.notifications.AuthEmailEvent
import com.neuropoligon.domain.notifications.AuthEmailNotifier
import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.platform.SecureStorage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Auth-слой: гостевой режим по умолчанию; при настройке Supabase (README) — расширяется.
 * MVP: локальная сессия после успешного ввода учётных данных (без отправки пароля в лог).
 */
public class SupabaseAuthService(
    private val secureStorage: SecureStorage,
    @Suppress("UnusedPrivateProperty")
    private val progressRepository: ProgressRepository,
    private val emailNotifier: AuthEmailNotifier,
) : AuthService {
    private val state = MutableStateFlow<AuthState>(AuthState.Guest)

    override val currentUser: Flow<AuthState> = state.asStateFlow()

    public suspend fun restoreSessionIfNeeded() {
        restoreSession()
    }

    override fun isConfigured(): Boolean = false

    override suspend fun signUpWithEmail(email: String, password: String): Result<Unit> {
        if (email.isBlank() || password.length < 6) {
            return Result.failure(IllegalArgumentException("Почта и пароль (мин. 6 символов) обязательны."))
        }
        saveSession(email)
        emailNotifier.notifyAdmin(AuthEmailEvent.SignUp, email)
        return Result.success(Unit)
    }

    override suspend fun signInWithEmail(email: String, password: String): Result<Unit> {
        if (email.isBlank() || password.isBlank()) {
            return Result.failure(IllegalArgumentException("Введите почту и пароль."))
        }
        saveSession(email)
        emailNotifier.notifyAdmin(AuthEmailEvent.SignIn, email)
        return Result.success(Unit)
    }

    override suspend fun sendMagicLink(email: String): Result<Unit> {
        if (email.isBlank()) return Result.failure(IllegalArgumentException("Укажите почту."))
        state.value = AuthState.PendingVerification(email)
        return Result.success(Unit)
    }

    override suspend fun verifyOtp(email: String, token: String): Result<Unit> {
        if (token.length < 4) return Result.failure(IllegalArgumentException("Неверный код."))
        saveSession(email)
        return Result.success(Unit)
    }

    override suspend fun signOut() {
        val email = (state.value as? AuthState.Authenticated)?.user?.email
        secureStorage.remove(KEY_SESSION)
        state.value = AuthState.Guest
        email?.let { emailNotifier.notifyAdmin(AuthEmailEvent.SignOut, it) }
    }

    private suspend fun saveSession(email: String) {
        secureStorage.set(KEY_SESSION, email)
        state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
    }

    private suspend fun restoreSession() {
        val email = secureStorage.get(KEY_SESSION) ?: return
        state.value = AuthState.Authenticated(AuthUser(id = email, email = email))
    }

    private companion object {
        private const val KEY_SESSION = "auth_session"
    }
}
