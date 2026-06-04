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

package com.neuropoligon.presentation.screens.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.ai.AiCapabilities
import com.neuropoligon.domain.ai.AiProvider
import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.presentation.components.NeuroPrimaryButton
import com.neuropoligon.presentation.components.NeuroSecondaryButton
import com.neuropoligon.presentation.components.NeuroTag
import com.neuropoligon.presentation.components.NeuroTextField
import com.neuropoligon.presentation.layout.AdaptiveContent
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun SettingsScreen(onAuthClick: () -> Unit, viewModel: SettingsViewModel = koinViewModel()) {
    val level by viewModel.level.collectAsState(); val apiKey by viewModel.apiKey.collectAsState(); val provider by viewModel.provider.collectAsState(); val message by viewModel.saveMessage.collectAsState(); val completed by viewModel.completedCount.collectAsState(); val repetitions by viewModel.repetitionCount.collectAsState(); val notes by viewModel.noteCount.collectAsState(); val bookmarks by viewModel.bookmarkCount.collectAsState()
    AdaptiveContent(Modifier.fillMaxSize()) {
        LazyColumn(contentPadding = PaddingValues(top = 18.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            item {
                Text("Профиль", style = MaterialTheme.typography.headlineMedium)
                Text("Настройте маршрут и подключите ИИ-лабораторию.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(Modifier.fillMaxWidth().padding(top = 14.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    ProfileStat("$completed", "уроков", Modifier.weight(1f)); ProfileStat("$repetitions", "карточек", Modifier.weight(1f)); ProfileStat("$notes", "заметок", Modifier.weight(1f)); ProfileStat("$bookmarks", "закладок", Modifier.weight(1f))
                }
            }
            item {
                Card(shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        NeuroTag("УЧЕБНЫЙ МАРШРУТ")
                        Text("Уровень объяснений", style = MaterialTheme.typography.titleLarge)
                        DifficultyLevel.entries.forEach { item ->
                            FilterChip(selected = level == item, onClick = { viewModel.setLevel(item) }, label = { Text(levelLabel(item)) }, modifier = Modifier.fillMaxWidth())
                        }
                    }
                }
            }
            item {
                Card(shape = MaterialTheme.shapes.large) {
                    Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        NeuroTag("AI-ЛАБОРАТОРИЯ")
                        Text("Модель для экспериментов", style = MaterialTheme.typography.titleLarge)
                        Text("Ключ хранится только на этом устройстве. Не используйте рабочие секреты или чужие данные.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        AiProvider.entries.filter { !viewModel.webWarning || AiCapabilities.of(it).availableOnWeb }.forEach { p -> FilterChip(selected = provider == p, onClick = { viewModel.updateProvider(p) }, label = { Text(p.name) }) }
                        NeuroTextField(apiKey, viewModel::updateApiKey, "API-ключ")
                        message?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary) }
                        NeuroPrimaryButton(text = "Сохранить подключение", onClick = viewModel::saveApiKey)
                    }
                }
            }
            item {
                Card(shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                    Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Прогресс на всех устройствах", style = MaterialTheme.typography.titleLarge)
                        Text("Войдите, чтобы синхронизировать обучение и восстановить результаты.")
                        NeuroSecondaryButton(text = "Вход и синхронизация", onClick = onAuthClick)
                    }
                }
            }
        }
    }
}

private fun levelLabel(level: DifficultyLevel): String = when (level) { DifficultyLevel.Zero -> "С нуля"; DifficultyLevel.Beginner -> "Начальный"; DifficultyLevel.Intermediate -> "Уверенный"; DifficultyLevel.Advanced -> "Продвинутый" }
@Composable private fun ProfileStat(value: String, label: String, modifier: Modifier) { Card(modifier, shape = MaterialTheme.shapes.medium) { Column(Modifier.padding(14.dp)) { Text(value, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.primary); Text(label, style = MaterialTheme.typography.bodySmall) } } }
