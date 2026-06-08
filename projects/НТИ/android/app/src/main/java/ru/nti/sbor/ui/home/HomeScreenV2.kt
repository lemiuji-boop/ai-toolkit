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

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.ui.theme.NtiTokens
import ru.nti.sbor.util.DateFormats

/** Главный экран — дизайн v2 (тёмный дашборд), полная функциональность. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreenV2(
    state: HomeUiState,
    onSearchChange: (String) -> Unit,
    onAdd: () -> Unit,
    onEdit: (Long) -> Unit,
    onOpenMenu: () -> Unit,
    onSettings: () -> Unit,
    onDelete: (Long) -> Unit,
) {
    val surface = Color(0xFF121418)
    val cardBg = Color(0xFF1E2329)
    val accentBlue = Color(0xFF4A9FE8)
    var deleteTarget by remember { mutableStateOf<LaborRecord?>(null) }
    val synced = state.records.count { it.syncStatus == SyncStatus.SYNCED }
    val errors = state.records.count { it.syncStatus == SyncStatus.ERROR }
    val progress = if (state.records.isEmpty()) 0f else synced.toFloat() / state.records.size

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        buildAnnotatedString {
                            withStyle(SpanStyle(color = Color.White)) { append("НТИ.") }
                            withStyle(SpanStyle(color = accentBlue, fontWeight = FontWeight.Bold)) {
                                append("Сбор")
                            }
                        },
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onOpenMenu) {
                        Icon(Icons.Default.Menu, contentDescription = "Меню", tint = Color.White)
                    }
                },
                actions = {
                    IconButton(onClick = onSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Настройки", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = surface),
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onAdd, containerColor = accentBlue) {
                Icon(Icons.Default.Add, contentDescription = "Добавить", tint = Color.White)
            }
        },
        containerColor = surface,
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding),
            contentPadding = PaddingValues(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF243044)),
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                ) {
                    Column(Modifier.padding(NtiTokens.SpacingMd)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Home, null, tint = accentBlue)
                            Column(Modifier.padding(start = NtiTokens.SpacingSm)) {
                                Text("Сводка записей", color = Color.White, fontWeight = FontWeight.SemiBold)
                                Text("НТИ.Сбор • офлайн", color = Color(0xFFB0B8C4), style = MaterialTheme.typography.bodySmall)
                            }
                        }
                        Row(
                            Modifier.fillMaxWidth().padding(top = NtiTokens.SpacingSm),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            StatChip("Всего", "${state.summaryCount}", Color.White)
                            StatChip("Синхр.", "$synced", accentBlue)
                            StatChip("Ошибки", "$errors", Color(0xFFE57373))
                        }
                        LinearProgressIndicator(
                            progress = { progress },
                            modifier = Modifier.fillMaxWidth().padding(top = NtiTokens.SpacingMd),
                            color = accentBlue,
                            trackColor = Color(0xFF3A4555),
                        )
                        Text(
                            "Сумма: ${state.summaryTotal} н/ч",
                            color = Color(0xFF8A939E),
                            style = MaterialTheme.typography.labelSmall,
                        )
                    }
                }
            }
            item {
                OutlinedTextField(
                    value = state.searchQuery,
                    onValueChange = onSearchChange,
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Поиск записей...", color = Color(0xFF8A939E)) },
                    leadingIcon = { Icon(Icons.Default.Search, null, tint = Color(0xFF8A939E)) },
                    trailingIcon = { Icon(Icons.Default.MoreVert, null, tint = Color(0xFF8A939E)) },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = accentBlue,
                        unfocusedBorderColor = Color(0xFF3A4555),
                        focusedTextColor = Color.White,
                        unfocusedTextColor = Color.White,
                    ),
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                    singleLine = true,
                )
            }
            item {
                Text("Последние записи", color = Color.White, fontWeight = FontWeight.SemiBold)
            }
            if (state.records.isEmpty()) {
                item { Text("Нет записей", color = Color(0xFF8A939E)) }
            }
            items(state.records, key = { it.id }) { record ->
                val isError = record.syncStatus == SyncStatus.ERROR
                Card(colors = CardDefaults.cardColors(containerColor = cardBg)) {
                    Row(
                        Modifier.fillMaxWidth().padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            if (isError) Icons.Default.Warning else Icons.Default.List,
                            null,
                            tint = if (isError) Color(0xFFE57373) else accentBlue,
                            modifier = Modifier.size(32.dp),
                        )
                        Column(Modifier.weight(1f).padding(horizontal = NtiTokens.SpacingSm)) {
                            Text(record.operation, color = Color.White, fontWeight = FontWeight.Medium)
                            Text(
                                "${record.product} • ${record.worker}",
                                color = Color(0xFF8A939E),
                                style = MaterialTheme.typography.bodySmall,
                            )
                            Text(
                                syncLabel(record.syncStatus),
                                color = if (isError) Color(0xFFE57373) else Color(0xFF81C784),
                                style = MaterialTheme.typography.labelMedium,
                            )
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                DateFormats.format(record.date),
                                color = Color(0xFF8A939E),
                                style = MaterialTheme.typography.labelSmall,
                            )
                            IconButton(onClick = { onEdit(record.id) }) {
                                Icon(Icons.Default.Edit, null, tint = accentBlue)
                            }
                            IconButton(onClick = { deleteTarget = record }) {
                                Icon(Icons.Default.Delete, null, tint = Color(0xFFE57373))
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

@Composable
private fun StatChip(label: String, value: String, valueColor: Color) {
    Column {
        Text(label, color = Color(0xFF8A939E), style = MaterialTheme.typography.labelSmall)
        Text(value, color = valueColor, fontWeight = FontWeight.Bold)
    }
}

private fun syncLabel(status: SyncStatus): String = when (status) {
    SyncStatus.LOCAL -> "Локально"
    SyncStatus.SYNCED -> "Отправлено"
    SyncStatus.ERROR -> "Ошибка"
}
