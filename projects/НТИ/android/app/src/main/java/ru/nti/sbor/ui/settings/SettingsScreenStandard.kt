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
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.theme.NtiTokens

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreenStandard(
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
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Настройки") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Назад")
                    }
                },
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(
            Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState())
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            Text("Профиль исполнителя", style = MaterialTheme.typography.titleLarge)
            OutlinedTextField(state.worker, onWorkerChange, label = { Text("ФИО") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(state.tabNumber, onTabChange, label = { Text("Табельный №") }, modifier = Modifier.fillMaxWidth())
            Button(onClick = onSaveProfile) { Text("Сохранить профиль") }
            Text("Тема", style = MaterialTheme.typography.titleLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm)) {
                FilterChip(selected = state.themeMode == ThemeMode.LIGHT, onClick = { onThemeSelect(ThemeMode.LIGHT) }, label = { Text("Светлая") })
                FilterChip(selected = state.themeMode == ThemeMode.DARK, onClick = { onThemeSelect(ThemeMode.DARK) }, label = { Text("Тёмная") })
                FilterChip(selected = state.themeMode == ThemeMode.SYSTEM, onClick = { onThemeSelect(ThemeMode.SYSTEM) }, label = { Text("Системная") })
            }
            Text("Сервер НТИ", style = MaterialTheme.typography.titleLarge)
            OutlinedTextField(
                state.serverUrl,
                onServerUrlChange,
                label = { Text("Адрес сервера (http:// или https://)") },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("http://192.168.1.10:8010") },
            )
            OutlinedTextField(state.serverToken, onServerTokenChange, label = { Text("Токен устройства") }, modifier = Modifier.fillMaxWidth())
            Button(onClick = onSaveServer) { Text("Сохранить настройки сервера") }
            Button(onClick = onCheckConnection, enabled = !state.isBusy) { Text("Проверить соединение") }
            Button(onClick = onSync, enabled = !state.isBusy) { Text("Синхронизировать записи") }
            Button(onClick = onPullOperations, enabled = !state.isBusy) { Text("Обновить справочник с сервера") }
            Button(onClick = onImportCsv, enabled = !state.isBusy) { Text("Импорт справочника из CSV") }
            Text("Данные", style = MaterialTheme.typography.titleLarge)
            Button(onClick = onExportCsv, enabled = !state.isBusy) { Text("Выгрузить CSV") }
            Button(onClick = onRequestClear) { Text("Очистить все данные") }
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
