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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.List
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
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.nti.sbor.ui.theme.NtiTokens

/** Макет 1: главный экран, светлая тема (mockup_01_home_light). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Variant1HomeLightScreen() {
    val items = listOf(
        Triple("Токарная", "АБВГ.1234.001", Icons.Default.Settings),
        Triple("Сборочная", "АБВГ.5678.002", Icons.Default.Build),
    )
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
                    IconButton(onClick = {}) {
                        Icon(Icons.Default.Settings, contentDescription = "Настройки")
                    }
                },
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = {},
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
                        Modifier
                            .fillMaxWidth()
                            .padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            Modifier
                                .size(48.dp)
                                .clip(CircleShape)
                                .background(NtiTokens.AccentSteelBlue.copy(alpha = 0.15f)),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(
                                Icons.Default.List,
                                contentDescription = null,
                                tint = NtiTokens.AccentSteelBlue,
                            )
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
                                        "3",
                                        style = MaterialTheme.typography.headlineMedium,
                                        color = NtiTokens.AccentSteelBlue,
                                        fontWeight = FontWeight.Bold,
                                    )
                                }
                                HorizontalDivider(
                                    modifier = Modifier
                                        .height(48.dp)
                                        .padding(vertical = 4.dp),
                                )
                                Column {
                                    Text("Сумма", style = MaterialTheme.typography.labelMedium)
                                    Text(
                                        "2,00 н/ч",
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
                    value = "",
                    onValueChange = {},
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Поиск по операциям и деталям") },
                    leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                    singleLine = true,
                )
            }
            items(items) { (title, part, icon) ->
                Card(
                    elevation = CardDefaults.cardElevation(2.dp),
                    shape = RoundedCornerShape(NtiTokens.RadiusMd),
                ) {
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .padding(NtiTokens.SpacingMd),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            Modifier
                                .size(44.dp)
                                .clip(CircleShape)
                                .background(NtiTokens.AccentSteelBlue.copy(alpha = 0.12f)),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(icon, contentDescription = null, tint = NtiTokens.AccentSteelBlue)
                        }
                        Column(Modifier.weight(1f).padding(horizontal = NtiTokens.SpacingMd)) {
                            Text(title, fontWeight = FontWeight.SemiBold)
                            Text("Деталь: $part", style = MaterialTheme.typography.bodyMedium)
                            Text("Операций: 2", style = MaterialTheme.typography.labelMedium)
                        }
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowForward,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }
            }
            item { Spacer(Modifier.height(72.dp)) }
        }
    }
}
