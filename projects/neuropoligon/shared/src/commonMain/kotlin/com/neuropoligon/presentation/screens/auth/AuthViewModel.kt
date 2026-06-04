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

package com.neuropoligon.presentation.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.data.auth.HybridAuthService
import com.neuropoligon.domain.auth.AuthMode
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.auth.AuthState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public class AuthViewModel(
    private val authService: AuthService,
) : ViewModel() {
    private val hybrid: HybridAuthService? = authService as? HybridAuthService

    public val state: StateFlow<AuthState> = authService.currentUser
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), AuthState.Guest)

    public val authMode: StateFlow<AuthMode> = hybrid?.authMode
        ?.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), AuthMode.Backend)
        ?: MutableStateFlow(AuthMode.Backend).asStateFlow()

    public val localVerificationCode: StateFlow<String?> = hybrid?.localVerificationCode
        ?.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
        ?: MutableStateFlow<String?>(null).asStateFlow()

    private val _statusMessage = MutableStateFlow<String?>(null)
    public val statusMessage: StateFlow<String?> = _statusMessage.asStateFlow()

    private val _authServerUrl = MutableStateFlow("")
    public val authServerUrl: StateFlow<String> = _authServerUrl.asStateFlow()

    private val _loading = MutableStateFlow(false)
    public val loading: StateFlow<Boolean> = _loading.asStateFlow()

    init {
        viewModelScope.launch {
            _authServerUrl.value = hybrid?.getApiBaseUrl().orEmpty()
        }
    }

    public fun updateAuthServerUrl(value: String) {
        _authServerUrl.value = value
    }

    public fun saveAuthServerUrl(onResult: (String?) -> Unit) {
        viewModelScope.launch {
            hybrid?.setApiBaseUrl(_authServerUrl.value)
            onResult(null)
            _statusMessage.value = "URL сервера сохранён"
        }
    }

    public fun testServer(onResult: (String?) -> Unit) {
        viewModelScope.launch {
            _loading.value = true
            hybrid?.setApiBaseUrl(_authServerUrl.value)
            val result = hybrid?.testBackendConnection()
            _loading.value = false
            result?.fold(
                onSuccess = {
                    _statusMessage.value = it
                    onResult(null)
                },
                onFailure = {
                    val msg = it.message ?: "Сервер недоступен"
                    _statusMessage.value = msg
                    onResult(msg)
                },
            ) ?: onResult("Сервис авторизации не инициализирован")
        }
    }

    public fun signIn(email: String, password: String, onResult: (String?) -> Unit) {
        runAuth(onResult) { authService.signInWithEmail(email, password) }
    }

    public fun signUp(email: String, password: String, onResult: (String?) -> Unit) {
        runAuth(onResult) { authService.signUpWithEmail(email, password) }
    }

    public fun verify(email: String, code: String, onResult: (String?) -> Unit) {
        runAuth(onResult) { authService.verifyOtp(email, code) }
    }

    public fun resendCode(email: String, onResult: (String?) -> Unit) {
        viewModelScope.launch {
            _loading.value = true
            val result = hybrid?.resendVerification(email)
                ?: authService.sendMagicLink(email)
            _loading.value = false
            result.fold(
                onSuccess = {
                    _statusMessage.value = "Код отправлен"
                    onResult(null)
                },
                onFailure = {
                    val msg = it.message ?: "Не удалось отправить код"
                    _statusMessage.value = msg
                    onResult(msg)
                },
            )
        }
    }

    public fun signOut() {
        viewModelScope.launch {
            authService.signOut()
            _statusMessage.value = "Вы вышли из аккаунта"
        }
    }

    private fun runAuth(onResult: (String?) -> Unit, block: suspend () -> Result<Unit>) {
        viewModelScope.launch {
            _loading.value = true
            block().fold(
                onSuccess = {
                    _loading.value = false
                    _statusMessage.value = "Готово"
                    onResult(null)
                },
                onFailure = {
                    _loading.value = false
                    val msg = it.message ?: "Ошибка"
                    _statusMessage.value = msg
                    onResult(msg)
                },
            )
        }
    }
}
