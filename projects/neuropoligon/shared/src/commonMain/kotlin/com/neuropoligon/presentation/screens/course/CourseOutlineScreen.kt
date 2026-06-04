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

package com.neuropoligon.presentation.screens.course

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.Module
import com.neuropoligon.presentation.components.NeuroSecondaryButton
import com.neuropoligon.presentation.components.NeuroTag
import com.neuropoligon.presentation.layout.AdaptiveContent
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun CourseOutlineScreen(
    onLessonClick: (String, String) -> Unit,
    onBack: () -> Unit,
    viewModel: CourseOutlineViewModel = koinViewModel(),
) {
    val track by viewModel.track.collectAsState()
    val chapters by viewModel.chapters.collectAsState()
    val completed by viewModel.completedModuleIds.collectAsState()
    val lessons = chapters.flatMap { it.lessons }
    val fraction = if (lessons.isEmpty()) 0f else completed.count { id -> lessons.any { it.id == id } }.toFloat() / lessons.size
    AdaptiveContent(Modifier.fillMaxSize()) {
        LazyColumn(contentPadding = PaddingValues(top = 18.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            item {
                NeuroSecondaryButton("Назад", onClick = onBack)
                Text("Карта навыков", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.padding(top = 16.dp))
                Text(track?.title ?: "Загрузка маршрута…", color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(Modifier.fillMaxWidth().padding(top = 12.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${completed.size} завершено", color = MaterialTheme.colorScheme.primary)
                    Text("${lessons.size} занятий")
                }
                LinearProgressIndicator(progress = { fraction }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp))
            }
            chapters.forEach { chapter ->
                item {
                    Text(chapter.title, style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(top = 12.dp))
                }
                itemsIndexed(chapter.lessons, key = { _, item -> item.id }) { index, lesson ->
                    SkillLessonCard(index + 1, lesson, completed.contains(lesson.id)) { track?.id?.let { onLessonClick(it, lesson.id) } }
                }
            }
        }
    }
}

@Composable
private fun SkillLessonCard(number: Int, lesson: Module, done: Boolean, onClick: () -> Unit) {
    Card(
        Modifier.fillMaxWidth().clickable(onClick = onClick),
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(containerColor = if (done) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface),
    ) {
        Row(Modifier.padding(16.dp), horizontalArrangement = Arrangement.spacedBy(14.dp)) {
            NeuroTag(if (done) "Готово" else number.toString())
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(lesson.title, style = MaterialTheme.typography.titleMedium)
                lesson.summary?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                Text("${lesson.durationMinutes ?: 7} мин · теория + практика", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
            }
        }
    }
}
