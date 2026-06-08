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
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Share
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.nti.sbor.ui.theme.NtiTokens

/** Макет 4: настройки (mockup_04_settings). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Variant4SettingsScreen() {
    val bg = Color(0xFFF0F2F5)
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Настройки", fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = {}) {
                        Icon(Icons.Default.Menu, contentDescription = "Меню", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = NtiTokens.AccentSteelBlue,
                    titleContentColor = Color.White,
                ),
            )
        },
        containerColor = bg,
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            SectionTitle(Icons.Default.Person, "Профиль")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Column(Modifier.padding(NtiTokens.SpacingMd)) {
                    ProfileRow(Icons.Default.Person, "ФИО", "Иванов Иван Иванович")
                    HorizontalDivider(Modifier.padding(vertical = NtiTokens.SpacingSm))
                    ProfileRow(Icons.Default.Info, "Табельный", "123456")
                }
            }

            SectionTitle(Icons.Default.Star, "Тема")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Row(
                    Modifier
                        .fillMaxWidth()
                        .padding(NtiTokens.SpacingSm),
                    horizontalArrangement = Arrangement.spacedBy(NtiTokens.SpacingSm),
                ) {
                    ThemeSegment(
                        label = "Светлая",
                        icon = Icons.Default.Star,
                        selected = true,
                        modifier = Modifier.weight(1f),
                    )
                    ThemeSegment(
                        label = "Тёмная",
                        icon = Icons.Default.Settings,
                        selected = false,
                        modifier = Modifier.weight(1f),
                    )
                }
            }

            SectionTitle(Icons.Default.Settings, "Сервер НТИ")
            Card(shape = RoundedCornerShape(NtiTokens.RadiusMd)) {
                Column(
                    Modifier.padding(NtiTokens.SpacingMd),
                    verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
                ) {
                    OutlinedTextField(
                        value = "https://nti.example.ru/api",
                        onValueChange = {},
                        label = { Text("URL") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                    )
                    OutlinedTextField(
                        value = "••••••••••••",
                        onValueChange = {},
                        label = { Text("Токен") },
                        modifier = Modifier.fillMaxWidth(),
                        trailingIcon = {
                            Icon(Icons.Default.Info, contentDescription = "Показать токен")
                        },
                        singleLine = true,
                    )
                    Button(
                        onClick = {},
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = NtiTokens.AccentSteelBlue),
                    ) {
                        Icon(Icons.Default.Check, contentDescription = null, tint = Color.White)
                        Text("Проверить соединение", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                    Button(
                        onClick = {},
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = NtiTokens.AccentSteelBlue.copy(alpha = 0.12f),
                            contentColor = NtiTokens.AccentSteelBlue,
                        ),
                    ) {
                        Icon(Icons.Default.Share, contentDescription = null)
                        Text("Выгрузить CSV", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                    OutlinedButton(
                        onClick = {},
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color(0xFFD32F2F)),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFD32F2F)),
                    ) {
                        Icon(Icons.Default.Delete, contentDescription = null)
                        Text("Очистить данные", Modifier.padding(start = NtiTokens.SpacingSm))
                    }
                }
            }
            Spacer(Modifier.height(NtiTokens.SpacingLg))
        }
    }
}

@Composable
private fun SectionTitle(icon: ImageVector, title: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, contentDescription = null, tint = NtiTokens.AccentSteelBlue)
        Text(title, Modifier.padding(start = NtiTokens.SpacingSm), fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun ProfileRow(icon: ImageVector, label: String, value: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        Column(Modifier.padding(start = NtiTokens.SpacingMd)) {
            Text(label, style = MaterialTheme.typography.labelMedium)
            Text(value, style = MaterialTheme.typography.bodyLarge)
        }
    }
}

@Composable
private fun ThemeSegment(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    modifier: Modifier = Modifier,
) {
    val border = if (selected) NtiTokens.AccentSteelBlue else Color(0xFFE0E0E0)
    val bg = if (selected) NtiTokens.AccentSteelBlue.copy(alpha = 0.1f) else Color.White
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(NtiTokens.RadiusSm),
        color = bg,
        border = BorderStroke(1.dp, border),
        onClick = {},
    ) {
        Row(
            Modifier.padding(NtiTokens.SpacingMd),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            Icon(icon, contentDescription = null, tint = if (selected) NtiTokens.AccentSteelBlue else Color.Gray)
            Text(
                label,
                Modifier.padding(start = NtiTokens.SpacingXs),
                color = if (selected) NtiTokens.AccentSteelBlue else Color.Gray,
            )
        }
    }
}
