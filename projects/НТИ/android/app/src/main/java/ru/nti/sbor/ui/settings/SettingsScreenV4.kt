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

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.theme.NtiTokens

/** Настройки — дизайн v4, полная функциональность. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreenV4(
    state: SettingsUiState,
    onBack: () -> Unit,
    onWorkerChange: (String) -> Unit,
    onTabChange: (String) -> Unit,
    onSaveProfile: () -> Unit,
    onThemeSelect: (ThemeMode) -> Unit,
    onServerUrlChange: (String) -> Unit,
    onServerTokenChange: (String) -> Unit,
    onSaveServer: () -> Unit,
    onCheckConnection: () -> Unit,
    onSync: () -> Unit,
    onPullOperations: () -> Unit,
    onImportCsv: () -> Unit,
    onExportCsv: () -> Unit,
    onRequestClear: () -> Unit,
    onConfirmClear: () -> Unit,
    onCancelClear: () -> Unit,
    snackbarHostState: SnackbarHostState,
) {
    val bg = Color(0xFFF0F2F5)
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Настройки", fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Назад", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = NtiTokens.AccentSteelBlue,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White,
                ),
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = bg,
    ) { padding ->
        Column(
            Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState())
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            V4SectionTitle(Icons.Default.Person, "Профиль")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Column(Modifier.padding(NtiTokens.SpacingMd), verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm)) {
                    OutlinedTextField(
                        value = state.worker,
                        onValueChange = onWorkerChange,
                        label = { Text("ФИО") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = state.tabNumber,
                        onValueChange = onTabChange,
                        label = { Text("Табельный") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Button(onClick = onSaveProfile, modifier = Modifier.fillMaxWidth()) {
                        Text("Сохранить профиль")
                    }
                }
            }

            V4SectionTitle(Icons.Default.Star, "Тема")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Row(
                    Modifier.fillMaxWidth().padding(NtiTokens.SpacingSm),
                    horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm),
                ) {
                    V4ThemeSegment("Светлая", Icons.Default.Star, state.themeMode == ThemeMode.LIGHT, {
                        onThemeSelect(ThemeMode.LIGHT)
                    }, Modifier.weight(1f))
                    V4ThemeSegment("Тёмная", Icons.Default.Settings, state.themeMode == ThemeMode.DARK, {
                        onThemeSelect(ThemeMode.DARK)
                    }, Modifier.weight(1f))
                }
            }

            V4SectionTitle(Icons.Default.Settings, "Сервер НТИ")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Column(
                    Modifier.padding(NtiTokens.SpacingMd),
                    verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
                ) {
                    OutlinedTextField(
                        value = state.serverUrl,
                        onValueChange = onServerUrlChange,
                        label = { Text("URL") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                    )
                    OutlinedTextField(
                        value = state.serverToken,
                        onValueChange = onServerTokenChange,
                        label = { Text("Токен") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                    )
                    Button(
                        onClick = onSaveServer,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = NtiTokens.AccentSteelBlue),
                    ) {
                        Text("Сохранить сервер")
                    }
                    Button(
                        onClick = onCheckConnection,
                        enabled = !state.isBusy,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = NtiTokens.AccentSteelBlue),
                    ) {
                        Icon(Icons.Default.Check, null, tint = Color.White)
                        Text("Проверить соединение", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                    Button(
                        onClick = onSync,
                        enabled = !state.isBusy,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Синхронизировать записи")
                    }
                    Button(
                        onClick = onPullOperations,
                        enabled = !state.isBusy,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Справочник с сервера")
                    }
                    Button(
                        onClick = onImportCsv,
                        enabled = !state.isBusy,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text("Импорт справочника (CSV)")
                    }
                    Button(
                        onClick = onExportCsv,
                        enabled = !state.isBusy,
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = NtiTokens.AccentSteelBlue.copy(alpha = 0.12f),
                            contentColor = NtiTokens.AccentSteelBlue,
                        ),
                    ) {
                        Icon(Icons.Default.Share, null)
                        Text("Выгрузить CSV", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                    OutlinedButton(
                        onClick = onRequestClear,
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color(0xFFD32F2F)),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFD32F2F)),
                    ) {
                        Icon(Icons.Default.Delete, null)
                        Text("Очистить данные", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                }
            }
            Spacer(Modifier.height(NtiTokens.SpacingLg))
        }
    }
    if (state.confirmClear) {
        AlertDialog(
            onDismissRequest = onCancelClear,
            title = { Text("Очистить все данные?") },
            text = { Text("Будут удалены все записи и профиль.") },
            confirmButton = { TextButton(onClick = onConfirmClear) { Text("Удалить") } },
            dismissButton = { TextButton(onClick = onCancelClear) { Text("Отмена") } },
        )
    }
}

@Composable
private fun V4SectionTitle(icon: ImageVector, title: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = NtiTokens.AccentSteelBlue)
        Text(title, Modifier.padding(start = NtiTokens.SpacingSm), fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun V4ThemeSegment(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val border = if (selected) NtiTokens.AccentSteelBlue else Color(0xFFE0E0E0)
    val bg = if (selected) NtiTokens.AccentSteelBlue.copy(alpha = 0.1f) else Color.White
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(NtiTokens.RadiusSm),
        color = bg,
        border = BorderStroke(1.dp, border),
        onClick = onClick,
    ) {
        Row(
            Modifier.padding(NtiTokens.SpacingMd),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            Icon(icon, null, tint = if (selected) NtiTokens.AccentSteelBlue else Color.Gray)
            Text(label, Modifier.padding(start = NtiTokens.SpacingXs), color = if (selected) NtiTokens.AccentSteelBlue else Color.Gray)
        }
    }
}
