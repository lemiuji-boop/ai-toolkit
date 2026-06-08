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

package ru.nti.sbor.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import ru.nti.sbor.AppContainer
import ru.nti.sbor.auth.AuthResult

data class LoginUiState(
    val username: String = "",
    val password: String = "",
    val isBusy: Boolean = false,
    val error: String? = null,
)

class LoginViewModel(private val container: AppContainer) : ViewModel() {
    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    fun updateUsername(v: String) = _state.update { it.copy(username = v, error = null) }
    fun updatePassword(v: String) = _state.update { it.copy(password = v, error = null) }

    fun login(onSuccess: () -> Unit) {
        viewModelScope.launch {
            _state.update { it.copy(isBusy = true, error = null) }
            when (val result = container.authRepository.login(_state.value.username, _state.value.password)) {
                is AuthResult.Success -> {
                    _state.update { it.copy(isBusy = false) }
                    onSuccess()
                }
                is AuthResult.Error -> {
                    _state.update { it.copy(isBusy = false, error = result.message) }
                }
            }
        }
    }
}

class LoginViewModelFactory(private val container: AppContainer) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(LoginViewModel::class.java)) {
            return LoginViewModel(container) as T
        }
        throw IllegalArgumentException("Unknown ViewModel")
    }
}
