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

package com.neuropoligon.presentation.screens.module

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun ModuleListScreen(
    trackId: String,
    onModuleClick: (String) -> Unit,
    onBack: () -> Unit,
    viewModel: ModuleListViewModel = koinViewModel(),
) {
    LaunchedEffect(trackId) { viewModel.load(trackId) }
    val track by viewModel.track.collectAsState()
    val completed by viewModel.completedModuleIds.collectAsState()
    Column(Modifier.fillMaxSize().padding(16.dp)) {
        IconButton(onClick = onBack) { Text("←") }
        Text(track?.title ?: "Модули")
        LazyColumn {
            items(track?.modules.orEmpty(), key = { it.id }) { module ->
                Card(
                    Modifier.fillMaxWidth().padding(vertical = 4.dp).clickable { onModuleClick(module.id) },
                ) {
                    Column(Modifier.padding(12.dp)) {
                        Text(module.title)
                        if (completed.contains(module.id)) Text("✓ Пройдено")
                    }
                }
            }
        }
    }
}
