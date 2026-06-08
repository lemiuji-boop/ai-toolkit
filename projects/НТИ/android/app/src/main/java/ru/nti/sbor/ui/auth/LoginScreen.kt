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

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import ru.nti.sbor.ui.design.NtiV2BrandTitle
import ru.nti.sbor.ui.design.NtiV2Design
import ru.nti.sbor.ui.design.NtiV2PrimaryButton
import ru.nti.sbor.ui.design.NtiV2TextField
import ru.nti.sbor.ui.theme.AccessibleV2Colors
import ru.nti.sbor.ui.theme.NtiTokens

@Composable
fun LoginScreen(
    viewModel: LoginViewModel,
    onLoggedIn: () -> Unit,
) {
    val state by viewModel.state.collectAsState()
    Scaffold(containerColor = AccessibleV2Colors.surface()) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(NtiTokens.SpacingLg),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            NtiV2BrandTitle()
            Spacer(Modifier.height(NtiTokens.SpacingSm))
            Text(
                "Вход",
                color = NtiV2Design.TextSecondary,
                fontWeight = FontWeight.Medium,
            )
            Spacer(Modifier.height(NtiTokens.SpacingXl))
            NtiV2TextField(
                value = state.username,
                onValueChange = viewModel::updateUsername,
                label = "Логин",
            )
            Spacer(Modifier.height(NtiTokens.SpacingMd))
            NtiV2TextField(
                value = state.password,
                onValueChange = viewModel::updatePassword,
                label = "Пароль",
                singleLine = true,
                visualTransformation = PasswordVisualTransformation(),
            )
            state.error?.let { msg ->
                Spacer(Modifier.height(NtiTokens.SpacingSm))
                Text(msg, color = NtiV2Design.Error)
            }
            Spacer(Modifier.height(NtiTokens.SpacingLg))
            if (state.isBusy) {
                CircularProgressIndicator(color = AccessibleV2Colors.accent())
            } else {
                NtiV2PrimaryButton("Войти", onClick = { viewModel.login(onLoggedIn) })
            }
        }
    }
}
