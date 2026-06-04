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

package com.neuropoligon.presentation.screens.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.presentation.components.NeuroTag
import kotlinx.coroutines.launch
import org.koin.compose.koinInject

@Composable
public fun OnboardingScreen(onDone: () -> Unit) {
    val settings: com.neuropoligon.domain.settings.SettingsRepository = koinInject()
    val scope = rememberCoroutineScope()
    Column(Modifier.fillMaxSize().padding(22.dp), verticalArrangement = Arrangement.Center) {
        NeuroTag("ПЕРСОНАЛЬНЫЙ СТАРТ")
        Text("Научись работать с ИИ, а не просто читать о нем", style = MaterialTheme.typography.headlineLarge, modifier = Modifier.padding(top = 16.dp))
        Text("Выбери свой опыт. Мы настроим сложность и дадим первую практическую миссию.", style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(top = 10.dp, bottom = 22.dp))
        DifficultyLevel.entries.forEach { level ->
            val (title, subtitle) = when (level) {
                DifficultyLevel.Zero -> "Начинаю с нуля" to "Понятно, спокойно, без технических слов"
                DifficultyLevel.Beginner -> "Уже пробовал чат-боты" to "Научусь получать стабильный результат"
                DifficultyLevel.Intermediate -> "Использую ИИ в работе" to "Автоматизация, документы и агенты"
                DifficultyLevel.Advanced -> "Создаю свои решения" to "API, RAG, локальные модели и оценка"
            }
            Card(
                onClick = { scope.launch { settings.setDifficultyLevel(level); settings.setOnboardingCompleted(true); onDone() } },
                modifier = Modifier.fillMaxWidth().padding(vertical = 5.dp),
                shape = MaterialTheme.shapes.medium,
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            ) {
                Column(Modifier.padding(16.dp)) {
                    Text(title, style = MaterialTheme.typography.titleMedium)
                    Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
