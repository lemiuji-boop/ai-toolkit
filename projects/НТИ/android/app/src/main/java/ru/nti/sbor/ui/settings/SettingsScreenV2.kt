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

package ru.nti.sbor.ui.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.design.NtiV2SectionCard
import ru.nti.sbor.ui.theme.AccessibleV2Colors
import ru.nti.sbor.ui.theme.NtiTokens

/** Настройки интерфейса для пользователя (без сервера и синхронизации). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreenV2(
    state: SettingsUiState,
    onBack: () -> Unit,
    onThemeSelect: (ThemeMode) -> Unit,
    onFontScaleSelect: (Float) -> Unit,
    onHighContrastChange: (Boolean) -> Unit,
    onLargeTouchChange: (Boolean) -> Unit,
    snackbarHostState: SnackbarHostState,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Оформление", color = AccessibleV2Colors.textPrimary()) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад",
                            tint = AccessibleV2Colors.textPrimary(),
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = AccessibleV2Colors.surface()),
            )
        },
        containerColor = AccessibleV2Colors.surface(),
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(
            Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState())
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            NtiV2SectionCard("Тема") {
                Row(horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm)) {
                    FilterChip(
                        selected = state.themeMode == ThemeMode.LIGHT,
                        onClick = { onThemeSelect(ThemeMode.LIGHT) },
                        label = { Text("Светлая") },
                    )
                    FilterChip(
                        selected = state.themeMode == ThemeMode.DARK,
                        onClick = { onThemeSelect(ThemeMode.DARK) },
                        label = { Text("Тёмная") },
                    )
                    FilterChip(
                        selected = state.themeMode == ThemeMode.SYSTEM,
                        onClick = { onThemeSelect(ThemeMode.SYSTEM) },
                        label = { Text("Системная") },
                    )
                }
            }
            NtiV2SectionCard("Размер шрифта") {
                Row(horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm)) {
                    FontScaleChip("Обычный", 1f, state.fontScale, onFontScaleSelect)
                    FontScaleChip("Крупный", 1.25f, state.fontScale, onFontScaleSelect)
                    FontScaleChip("Большой", 1.5f, state.fontScale, onFontScaleSelect)
                    FontScaleChip("Очень крупный", 2f, state.fontScale, onFontScaleSelect)
                }
            }
            NtiV2SectionCard("Для слабовидящих") {
                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("Высокий контраст", color = AccessibleV2Colors.textPrimary())
                    Switch(checked = state.highContrast, onCheckedChange = onHighContrastChange)
                }
                Row(
                    Modifier.fillMaxWidth().padding(top = NtiTokens.SpacingSm),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("Крупные кнопки", color = AccessibleV2Colors.textPrimary())
                    Switch(checked = state.largeTouchTargets, onCheckedChange = onLargeTouchChange)
                }
            }
        }
    }
}

@Composable
private fun FontScaleChip(
    label: String,
    scale: Float,
    current: Float,
    onSelect: (Float) -> Unit,
) {
    FilterChip(
        selected = current == scale,
        onClick = { onSelect(scale) },
        label = { Text(label) },
    )
}
