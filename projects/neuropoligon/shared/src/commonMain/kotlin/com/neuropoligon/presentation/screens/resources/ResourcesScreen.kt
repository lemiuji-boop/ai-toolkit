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

package com.neuropoligon.presentation.screens.resources

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.platform.openUrl
import com.neuropoligon.presentation.components.NeuroTag
import com.neuropoligon.presentation.layout.AdaptiveContent
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun ResourcesScreen(viewModel: ResourcesViewModel = koinViewModel()) {
    val resources by viewModel.resources.collectAsState()
    val query by viewModel.query.collectAsState()
    AdaptiveContent(Modifier.fillMaxSize()) {
        LazyColumn(contentPadding = PaddingValues(top = 18.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            item {
                Text("Библиотека ИИ", style = MaterialTheme.typography.headlineMedium)
                Text("Проверенные инструменты и материалы для следующего шага.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                OutlinedTextField(query, viewModel::search, Modifier.fillMaxWidth().padding(top = 14.dp), label = { Text("Найти инструмент или тему") }, singleLine = true)
            }
            if (resources.isEmpty()) item { Text("Ничего не найдено. Попробуйте другой запрос.") }
            items(resources, key = { it.id }) { entry ->
                Card(
                    Modifier.fillMaxWidth().clickable { openUrl(entry.officialUrl) },
                    shape = MaterialTheme.shapes.medium,
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        NeuroTag(entry.category)
                        Text(entry.name, style = MaterialTheme.typography.titleMedium)
                        Text(entry.whatItIs, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("Подходит для: ${entry.useFor}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
                    }
                }
            }
        }
    }
}
