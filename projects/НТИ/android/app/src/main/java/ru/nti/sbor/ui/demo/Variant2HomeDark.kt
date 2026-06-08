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

package ru.nti.sbor.ui.demo

import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Warning
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
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import ru.nti.sbor.ui.theme.NtiTokens

private data class DarkListItem(
    val title: String,
    val id: String,
    val worker: String,
    val status: String,
    val time: String,
    val isError: Boolean,
)

/** Макет 2: главный экран, тёмная тема (mockup_02_home_dark). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Variant2HomeDarkScreen() {
    val surface = Color(0xFF121418)
    val cardBg = Color(0xFF1E2329)
    val accentBlue = Color(0xFF4A9FE8)
    val listItems = listOf(
        DarkListItem("Сборка изделия А-12", "#1287", "Иванов И.И.", "Отправлено", "09:28", false),
        DarkListItem("Проверка узла Б-7", "#1286", "Петров П.П.", "Отправлено", "09:21", false),
        DarkListItem("Контроль качества", "#1285", "Сидоров С.С.", "Ошибка", "09:15", true),
        DarkListItem("Упаковка и маркировка", "#1284", "Иванов И.И.", "Отправлено", "09:10", false),
    )
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
                    IconButton(onClick = {}) {
                        Icon(Icons.Default.Menu, contentDescription = "Меню", tint = Color.White)
                    }
                },
                actions = {
                    IconButton(onClick = {}) {
                        Icon(Icons.Default.Notifications, contentDescription = "Уведомления", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = surface),
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = {}, containerColor = accentBlue) {
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
                            Icon(Icons.Default.Home, contentDescription = null, tint = accentBlue)
                            Column(Modifier.padding(start = NtiTokens.SpacingSm)) {
                                Text("ООО «МеталлПром»", color = Color.White, fontWeight = FontWeight.SemiBold)
                                Text("Цех №1 • Участок сборки", color = Color(0xFFB0B8C4), style = MaterialTheme.typography.bodySmall)
                            }
                        }
                        Text(
                            "Сводка за сегодня",
                            Modifier.padding(top = NtiTokens.SpacingMd),
                            color = Color.White,
                            fontWeight = FontWeight.Medium,
                        )
                        Row(
                            Modifier
                                .fillMaxWidth()
                                .padding(top = NtiTokens.SpacingSm),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            StatChip("Всего записей", "128", Color.White)
                            StatChip("Отправлено", "102", accentBlue)
                            StatChip("Ошибки", "6", Color(0xFFE57373))
                        }
                        LinearProgressIndicator(
                            progress = { 0.79f },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = NtiTokens.SpacingMd),
                            color = accentBlue,
                            trackColor = Color(0xFF3A4555),
                        )
                        Row(
                            Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            Text("79%", color = accentBlue, style = MaterialTheme.typography.labelMedium)
                            Text("Обновлено 09:30", color = Color(0xFF8A939E), style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
            item {
                OutlinedTextField(
                    value = "",
                    onValueChange = {},
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Поиск записей...", color = Color(0xFF8A939E)) },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = Color(0xFF8A939E)) },
                    trailingIcon = { Icon(Icons.Default.Menu, contentDescription = null, tint = Color(0xFF8A939E)) },
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
            items(listItems) { item ->
                Card(colors = CardDefaults.cardColors(containerColor = cardBg)) {
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            if (item.isError) Icons.Default.Warning else Icons.Default.List,
                            contentDescription = null,
                            tint = if (item.isError) Color(0xFFE57373) else accentBlue,
                            modifier = Modifier.size(32.dp),
                        )
                        Column(Modifier.weight(1f).padding(horizontal = NtiTokens.SpacingSm)) {
                            Text(item.title, color = Color.White, fontWeight = FontWeight.Medium)
                            Text("${item.id} • ${item.worker}", color = Color(0xFF8A939E), style = MaterialTheme.typography.bodySmall)
                            Text(
                                item.status,
                                color = if (item.isError) Color(0xFFE57373) else Color(0xFF81C784),
                                style = MaterialTheme.typography.labelMedium,
                            )
                        }
                        Column(horizontalAlignment = Alignment.End) {
                            Text(item.time, color = Color(0xFF8A939E), style = MaterialTheme.typography.labelSmall)
                            Icon(
                                Icons.AutoMirrored.Filled.ArrowForward,
                                contentDescription = null,
                                tint = Color(0xFF6A7580),
                            )
                        }
                    }
                }
            }
            item { Spacer(Modifier.height(72.dp)) }
        }
    }
}

@Composable
private fun StatChip(label: String, value: String, valueColor: Color) {
    Column {
        Text(label, color = Color(0xFF8A939E), style = MaterialTheme.typography.labelSmall)
        Text(value, color = valueColor, fontWeight = FontWeight.Bold)
    }
}
