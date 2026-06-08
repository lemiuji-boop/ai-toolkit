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

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.ui.theme.NtiTokens
import ru.nti.sbor.util.DateFormats

/** Главный экран — дизайн v1 (светлый), полная функциональность. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreenV1(
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
                title = { Text("НТИ.Сбор", fontWeight = FontWeight.SemiBold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = NtiTokens.AccentSteelBlue,
                    titleContentColor = Color.White,
                    actionIconContentColor = Color.White,
                ),
                actions = {
                    IconButton(onClick = onSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Настройки")
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = onAdd,
                containerColor = NtiTokens.AccentSteelBlue,
                contentColor = Color.White,
            ) {
                Icon(Icons.Default.Add, contentDescription = "Добавить")
            }
        },
        containerColor = Color(0xFFF0F2F5),
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding),
            contentPadding = PaddingValues(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            item {
                Card(
                    elevation = CardDefaults.cardElevation(4.dp),
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                ) {
                    Row(
                        Modifier.fillMaxWidth().padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            Modifier.size(48.dp).clip(CircleShape)
                                .background(NtiTokens.AccentSteelBlue.copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(Icons.Default.List, null, tint = NtiTokens.AccentSteelBlue)
                        }
                        Column(Modifier.padding(start = NtiTokens.SpacingMd)) {
                            Text("Сводка", style = MaterialTheme.typography.titleMedium)
                            Row(
                                Modifier.padding(top = NtiTokens.SpacingSm),
                                horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingLg),
                            ) {
                                Column {
                                    Text("Записей", style = MaterialTheme.typography.labelMedium)
                                    Text(
                                        "${state.summaryCount}",
                                        style = MaterialTheme.typography.headlineMedium,
                                        color = NtiTokens.AccentSteelBlue,
                                        fontWeight = FontWeight.Bold,
                                    )
                                }
                                HorizontalDivider(Modifier.height(48.dp).padding(vertical = 4.dp))
                                Column {
                                    Text("Сумма", style = MaterialTheme.typography.labelMedium)
                                    Text(
                                        "${state.summaryTotal} н/ч",
                                        style = MaterialTheme.typography.headlineSmall,
                                        color = NtiTokens.AccentSteelBlue,
                                        fontWeight = FontWeight.Bold,
                                    )
                                }
                            }
                        }
                    }
                }
            }
            item {
                OutlinedTextField(
                    value = state.searchQuery,
                    onValueChange = onSearchChange,
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Поиск по операциям и деталям") },
                    leadingIcon = { Icon(Icons.Default.Search, null) },
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                    singleLine = true,
                )
            }
            if (state.records.isEmpty()) {
                item {
                    Text(
                        "Нет записей. Нажмите + чтобы добавить.",
                        modifier = Modifier.padding(NtiTokens.SpacingMd),
                    )
                }
            }
            items(state.records, key = { it.id }) { record ->
                val icon = if (record.operation.contains("Сбор", true)) {
                    Icons.Default.Build
                } else {
                    Icons.Default.Build
                }
                Card(
                    elevation = CardDefaults.cardElevation(2.dp),
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                ) {
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .clickable { onEdit(record.id) }
                            .padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            Modifier.size(44.dp).clip(CircleShape)
                                .background(NtiTokens.AccentSteelBlue.copy(alpha = 0.12f)),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(icon, null, tint = NtiTokens.AccentSteelBlue)
                        }
                        Column(Modifier.weight(1f).padding(horizontal = NtiTokens.SpacingMd)) {
                            Text(record.operation, fontWeight = FontWeight.SemiBold)
                            Text("Изделие: ${record.product}", style = MaterialTheme.typography.bodyMedium)
                            Text(
                                "${record.value.toString().replace('.', ',')} ${record.unit.label} • ${DateFormats.format(record.date)}",
                                style = MaterialTheme.typography.labelMedium,
                            )
                            Text(syncLabel(record.syncStatus), style = MaterialTheme.typography.labelSmall)
                        }
                        Row {
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
            item { Spacer(Modifier.height(72.dp)) }
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
