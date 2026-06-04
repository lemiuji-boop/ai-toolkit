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

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.auth.AuthMode
import com.neuropoligon.domain.auth.AuthState
import com.neuropoligon.presentation.components.AnimatedScreenEntrance
import com.neuropoligon.presentation.components.NeuroErrorBanner
import com.neuropoligon.presentation.components.NeuroGradientHeader
import com.neuropoligon.presentation.components.NeuroInfoCard
import com.neuropoligon.presentation.components.NeuroPrimaryButton
import com.neuropoligon.presentation.components.NeuroSecondaryButton
import com.neuropoligon.presentation.components.NeuroTextField
import com.neuropoligon.presentation.theme.NeuroColors
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun AuthScreen(
    onBack: () -> Unit,
    viewModel: AuthViewModel = koinViewModel(),
) {
    val state by viewModel.state.collectAsState()
    val authMode by viewModel.authMode.collectAsState()
    val localCode by viewModel.localVerificationCode.collectAsState()
    val statusMessage by viewModel.statusMessage.collectAsState()
    val serverUrl by viewModel.authServerUrl.collectAsState()
    val loading by viewModel.loading.collectAsState()

    var tab by remember { mutableIntStateOf(0) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var fieldError by remember { mutableStateOf<String?>(null) }

    AnimatedScreenEntrance {
        Column(
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            NeuroGradientHeader(
                title = "Аккаунт",
                subtitle = "Синхронизация прогресса и доступ с любого устройства",
            )
            Column(Modifier.padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                NeuroSecondaryButton("← Назад", onClick = onBack)

                when (val s = state) {
                    is AuthState.Guest -> Text(
                        "Гостевой режим: курс доступен без входа.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    is AuthState.Authenticated -> Text(
                        "Вы вошли: ${s.user.email}",
                        color = NeuroColors.Success,
                        style = MaterialTheme.typography.titleMedium,
                    )
                    is AuthState.PendingVerification -> {
                        Text(
                            "Подтвердите почту: ${s.email}",
                            color = MaterialTheme.colorScheme.primary,
                            style = MaterialTheme.typography.titleMedium,
                        )
                        email = s.email
                        tab = 1
                    }
                }

                NeuroInfoCard {
                    Text("Сервер авторизации", style = MaterialTheme.typography.titleSmall)
                    NeuroTextField(
                        value = serverUrl,
                        onValueChange = viewModel::updateAuthServerUrl,
                        label = "URL (http://IP:8080)",
                    )
                    NeuroSecondaryButton(
                        text = "Проверить связь с сервером",
                        onClick = {
                            fieldError = null
                            viewModel.testServer { fieldError = it }
                        },
                        enabled = !loading,
                    )
                }

                if (authMode == AuthMode.Local) {
                    NeuroInfoCard {
                        Text(
                            "Сервер недоступен — включён локальный режим. Код подтверждения:",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            localCode ?: "—",
                            style = MaterialTheme.typography.headlineMedium,
                            color = MaterialTheme.colorScheme.primary,
                        )
                    }
                }

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(
                        selected = tab == 0,
                        onClick = { tab = 0 },
                        label = { Text("Вход") },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                        ),
                    )
                    FilterChip(
                        selected = tab == 1,
                        onClick = { tab = 1 },
                        label = { Text("Регистрация") },
                    )
                }

                NeuroTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = "Почта",
                )
                NeuroTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = "Пароль",
                )

                AnimatedVisibility(visible = tab == 1 || state is AuthState.PendingVerification, enter = fadeIn()) {
                    NeuroTextField(
                        value = code,
                        onValueChange = { code = it },
                        label = "Код из письма или с экрана",
                    )
                }

                AnimatedVisibility(visible = fieldError != null, enter = fadeIn()) {
                    fieldError?.let { NeuroErrorBanner(it) }
                }

                statusMessage?.let {
                    Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }

                if (tab == 0) {
                    NeuroPrimaryButton(
                        text = "Войти",
                        loading = loading,
                        onClick = {
                            fieldError = null
                            viewModel.signIn(email, password) { fieldError = it }
                        },
                    )
                } else {
                    NeuroPrimaryButton(
                        text = "Зарегистрироваться",
                        loading = loading,
                        onClick = {
                            fieldError = null
                            viewModel.saveAuthServerUrl { }
                            viewModel.signUp(email, password) { fieldError = it }
                        },
                    )
                    NeuroSecondaryButton(
                        text = "Подтвердить код",
                        enabled = !loading,
                        onClick = {
                            fieldError = null
                            viewModel.verify(email, code) { fieldError = it }
                        },
                    )
                    NeuroSecondaryButton(
                        text = "Отправить код ещё раз",
                        enabled = !loading,
                        onClick = {
                            fieldError = null
                            viewModel.resendCode(email) { fieldError = it }
                        },
                    )
                }

                NeuroSecondaryButton("Выйти", onClick = viewModel::signOut)
                NeuroSecondaryButton("Продолжить как гость", onClick = onBack)
            }
        }
    }
}
