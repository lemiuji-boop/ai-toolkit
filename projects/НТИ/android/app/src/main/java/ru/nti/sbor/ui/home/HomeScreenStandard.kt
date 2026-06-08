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

package ru.nti.sbor.ui.home

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.ui.theme.NtiTokens
import ru.nti.sbor.util.DateFormats

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreenStandard(
    state: HomeUiState,
    onSearchChange: (String) -> Unit,
    onAdd: () -> Unit,
    onEdit: (Long) -> Unit,
    onSettings: () -> Unit,
    onDelete: (Long) -> Unit,
) {
    var deleteTarget by remember { mutableStateOf<LaborRecord?>(null) }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("НТИ.Сбор") },
                actions = {
                    IconButton(onClick = onSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Настройки")
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onAdd) {
                Icon(Icons.Default.Add, contentDescription = "Добавить запись")
            }
        },
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding),
            contentPadding = PaddingValues(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm),
        ) {
            item {
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(NtiTokens.SpacingMd)) {
                        Text("Сводка", style = MaterialTheme.typography.titleLarge)
                        Text("Записей: ${state.summaryCount}")
                        Text("Сумма, н/ч: ${state.summaryTotal}")
                        Text("Средняя, н/ч: ${state.summaryAverage}")
                    }
                }
            }
            item {
                OutlinedTextField(
                    value = state.searchQuery,
                    onValueChange = onSearchChange,
                    label = { Text("Поиск") },
                    placeholder = { Text("Исполнитель, изделие, операция") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                )
            }
            if (state.records.isEmpty()) {
                item { Text("Нет записей. Нажмите + чтобы добавить.") }
            }
            items(state.records, key = { it.id }) { record ->
                Card(Modifier.fillMaxWidth()) {
                    Column(
                        Modifier
                            .fillMaxWidth()
                            .clickable { onEdit(record.id) }
                            .padding(NtiTokens.SpacingMd),
                    ) {
                        Text(record.operation, style = MaterialTheme.typography.titleLarge)
                        Text("Изделие: ${record.product}")
                        Text("Исполнитель: ${record.worker}")
                        Text("Трудоёмкость: ${record.value.toString().replace('.', ',')} ${record.unit.label}")
                        Text("Дата: ${DateFormats.format(record.date)}")
                        if (record.note.isNotBlank()) Text("Примечание: ${record.note}")
                        Text(syncLabel(record.syncStatus), style = MaterialTheme.typography.labelLarge)
                        Row(
                            horizontalArrangement = Arrangement.End,
                            modifier = Modifier.fillMaxWidth(),
                        ) {
                            IconButton(onClick = { onEdit(record.id) }) {
                                Icon(Icons.Default.Edit, contentDescription = "Редактировать")
                            }
                            IconButton(onClick = { deleteTarget = record }) {
                                Icon(Icons.Default.Delete, contentDescription = "Удалить")
                            }
                        }
                    }
                }
            }
        }
    }
    deleteTarget?.let { record ->
        AlertDialog(
            onDismissRequest = { deleteTarget = null },
            title = { Text("Удалить запись?") },
            text = { Text("${record.operation} — ${record.product}") },
            confirmButton = {
                TextButton(onClick = {
                    onDelete(record.id)
                    deleteTarget = null
                }) { Text("Удалить") }
            },
            dismissButton = {
                TextButton(onClick = { deleteTarget = null }) { Text("Отмена") }
            },
        )
    }
}

private fun syncLabel(status: SyncStatus): String = when (status) {
    SyncStatus.LOCAL -> "Локально"
    SyncStatus.SYNCED -> "Синхронизировано"
    SyncStatus.ERROR -> "Ошибка синхронизации"
}
