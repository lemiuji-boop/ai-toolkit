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

import com.neuropoligon.domain.auth.AuthMode
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.auth.AuthState
import io.ktor.client.plugins.HttpRequestTimeoutException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flatMapLatest

/**
 * Сначала backend; при сетевой ошибке — локальная авторизация (код на экране).
 */
@OptIn(ExperimentalCoroutinesApi::class)
public class HybridAuthService(
    private val backend: BackendEmailAuthService,
    private val local: LocalDeviceAuthService,
) : AuthService {
    private val _authMode = MutableStateFlow(AuthMode.Backend)

    public val authMode: Flow<AuthMode> = _authMode.asStateFlow()
    public val localVerificationCode: Flow<String?> = local.lastVerificationCode

    override val currentUser: Flow<AuthState> = _authMode.flatMapLatest { mode ->
        when (mode) {
            AuthMode.Local -> local.currentUser
            AuthMode.Backend -> backend.currentUser
        }
    }

    public suspend fun restoreSessionIfNeeded() {
        backend.restoreSessionIfNeeded()
        local.restoreSessionIfNeeded()
        _authMode.value = when {
            backend.peekState() is AuthState.Authenticated -> AuthMode.Backend
            local.peekState() is AuthState.Authenticated -> AuthMode.Local
            else -> AuthMode.Backend
        }
    }

    public suspend fun setApiBaseUrl(url: String) {
        backend.setApiBaseUrl(url)
    }

    public suspend fun getApiBaseUrl(): String = backend.getApiBaseUrl()

    public suspend fun testBackendConnection(): Result<String> = backend.ping()

    override fun isConfigured(): Boolean = true

    override suspend fun signUpWithEmail(email: String, password: String): Result<Unit> {
        val remote = backend.signUpWithEmail(email, password)
        if (remote.isSuccess) {
            _authMode.value = AuthMode.Backend
            return remote
        }
        if (!isNetworkError(remote.exceptionOrNull())) return remote
        val localResult = local.signUpWithEmail(email, password)
        if (localResult.isSuccess) _authMode.value = AuthMode.Local
        return localResult
    }

    override suspend fun signInWithEmail(email: String, password: String): Result<Unit> {
        val remote = backend.signInWithEmail(email, password)
        if (remote.isSuccess) {
            _authMode.value = AuthMode.Backend
            return remote
        }
        if (!isNetworkError(remote.exceptionOrNull())) return remote
        val localResult = local.signInWithEmail(email, password)
        if (localResult.isSuccess) _authMode.value = AuthMode.Local
        return localResult
    }

    override suspend fun sendMagicLink(email: String): Result<Unit> = resendVerification(email)

    public suspend fun resendVerification(email: String): Result<Unit> {
        if (_authMode.value == AuthMode.Local) return local.resendCode(email)
        val remote = backend.resendVerification(email)
        if (remote.isSuccess) return remote
        if (!isNetworkError(remote.exceptionOrNull())) return remote
        return local.resendCode(email)
    }

    override suspend fun verifyOtp(email: String, token: String): Result<Unit> {
        if (_authMode.value == AuthMode.Local) return local.verifyOtp(email, token)
        val remote = backend.verifyOtp(email, token)
        if (remote.isSuccess) {
            _authMode.value = AuthMode.Backend
            return remote
        }
        if (!isNetworkError(remote.exceptionOrNull())) return remote
        return local.verifyOtp(email, token)
    }

    override suspend fun signOut() {
        backend.signOut()
        local.signOut()
        _authMode.value = AuthMode.Backend
    }

}

internal fun isNetworkError(e: Throwable?): Boolean {
    if (e == null) return false
    if (e is HttpRequestTimeoutException) return true
    val msg = e.message.orEmpty().lowercase()
    return msg.contains("connection") ||
        msg.contains("unable to resolve") ||
        msg.contains("failed to connect") ||
        msg.contains("network") ||
        msg.contains("timeout") ||
        msg.contains("сервер недоступен") ||
        msg.contains("connectexception") ||
        msg.contains("unknownhost")
}
