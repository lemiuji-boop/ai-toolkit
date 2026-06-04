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

package com.neuropoligon.presentation.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.neuropoligon.presentation.components.NeuroPrimaryButton
import com.neuropoligon.presentation.components.NeuroSecondaryButton
import com.neuropoligon.presentation.components.NeuroSectionTitle
import com.neuropoligon.presentation.components.NeuroTag
import com.neuropoligon.presentation.layout.AdaptiveContent
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun HomeScreen(
    onStartLesson: (trackId: String, moduleId: String) -> Unit,
    onOpenOutline: (trackId: String) -> Unit,
    onAuthClick: () -> Unit,
    viewModel: HomeViewModel = koinViewModel(),
) {
    val track by viewModel.primaryTrack.collectAsState()
    val tracks by viewModel.tracks.collectAsState()
    val learningModes by viewModel.learningModes.collectAsState()
    val selectedMode by viewModel.learningModeId.collectAsState()
    val progress by viewModel.progressFraction.collectAsState()
    val streak by viewModel.streakDays.collectAsState()
    val total = track?.modules?.size ?: 0
    val done = (progress * total).toInt().coerceAtMost(total)

    AdaptiveContent(Modifier.fillMaxSize()) {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(top = 18.dp, bottom = 28.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            item {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Column {
                        Text("НЕЙРОПОЛИГОН", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
                        Text("Тренируй ИИ-навыки", style = MaterialTheme.typography.headlineMedium)
                    }
                    NeuroTag(if (streak > 0) "Серия  дн." else "Начни серию")
                }
            }
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color.Transparent),
                    shape = MaterialTheme.shapes.extraLarge,
                    modifier = Modifier.background(
                        Brush.linearGradient(listOf(Color(0xFF11132A), Color(0xFF5B5FEF), Color(0xFF8B5CF6))),
                        MaterialTheme.shapes.extraLarge,
                    ),
                ) {
                    Column(Modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        NeuroTag("МИССИЯ НА СЕГОДНЯ")
                        Text(track?.modules?.firstOrNull()?.title ?: "Первый шаг в ИИ", style = MaterialTheme.typography.headlineMedium, color = Color.White)
                        Text("Один короткий урок, практика и проверка. Примерно 7 минут.", style = MaterialTheme.typography.bodyLarge, color = Color.White.copy(alpha = .82f))
                        NeuroPrimaryButton(text = "Продолжить обучение", onClick = {
                            track?.let { onStartLesson(it.id, viewModel.firstLessonModuleId(it)) }
                        })
                    }
                }
            }
            item {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    StatCard("$done", "пройдено", Modifier.fillMaxWidth(0.31f))
                    StatCard("${total - done}", "впереди", Modifier.fillMaxWidth(0.45f))
                    StatCard("${tracks.size}", "треков", Modifier.fillMaxWidth())
                }
            }
            item {
                Card(shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                    Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            NeuroSectionTitle("Твой маршрут")
                            Text("${(progress * 100).toInt()}%", color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.titleMedium)
                        }
                        LinearProgressIndicator(progress = { progress.coerceIn(0f, 1f) }, modifier = Modifier.fillMaxWidth())
                        Text(track?.title ?: "Подбираем программу…", style = MaterialTheme.typography.titleMedium)
                        Text("Освой базу, научись писать сильные запросы и проверять ответы ИИ.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        NeuroSecondaryButton(text = "Открыть карту навыков", onClick = { track?.id?.let(onOpenOutline) })
                    }
                }
            }
            if (learningModes.isNotEmpty()) item {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    NeuroSectionTitle("Выбери темп")
                    learningModes.forEach { mode ->
                        Card(
                            onClick = { viewModel.setLearningMode(mode.id) },
                            shape = MaterialTheme.shapes.medium,
                            colors = CardDefaults.cardColors(containerColor = if (selectedMode == mode.id) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface),
                        ) {
                            Column(Modifier.fillMaxWidth().padding(16.dp)) {
                                Text(mode.title, style = MaterialTheme.typography.titleMedium)
                                Text(mode.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                }
            }
            item { NeuroSectionTitle("Специализации") }
            tracks.drop(1).forEach { extra ->
                item {
                    Card(onClick = { extra.modules.firstOrNull()?.let { onStartLesson(extra.id, it.id) } }, modifier = Modifier.fillMaxWidth(), shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
                        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            NeuroTag(if (extra.requiresApiKey) "С AI-ЛАБОРАТОРИЕЙ" else "ОФЛАЙН")
                            Text(extra.title, style = MaterialTheme.typography.titleLarge)
                            Text(extra.description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text(" занятий", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                        }
                    }
                }
            }
            item {
                NeuroSecondaryButton("Профиль и синхронизация", onClick = onAuthClick)
            }
        }
    }
}

@Composable
private fun StatCard(value: String, label: String, modifier: Modifier = Modifier) {
    Card(modifier, shape = MaterialTheme.shapes.medium, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Column(Modifier.padding(14.dp)) {
            Text(value, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.primary)
            Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
