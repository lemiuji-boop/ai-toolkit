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

package com.neuropoligon.presentation.screens.review

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.presentation.components.NeuroPrimaryButton
import com.neuropoligon.presentation.components.NeuroSecondaryButton
import com.neuropoligon.presentation.components.NeuroTag
import com.neuropoligon.presentation.layout.AdaptiveContent
import org.koin.compose.viewmodel.koinViewModel

@Composable
public fun ReviewScreen(viewModel: ReviewViewModel = koinViewModel()) {
    val cards by viewModel.cards.collectAsState()
    AdaptiveContent(Modifier.fillMaxSize()) {
        LazyColumn(contentPadding = PaddingValues(top = 18.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            item {
                Text("Практика памяти", style = MaterialTheme.typography.headlineMedium)
                Text("Короткие повторения появляются в нужный момент и помогают перенести знания в долговременную память.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(Modifier.fillMaxWidth().padding(top = 14.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    Summary("${cards.size}", "на сегодня", Modifier.weight(1f))
                    Summary("SM-2", "умный ритм", Modifier.weight(1f))
                }
            }
            if (cards.isEmpty()) item {
                Card(shape = MaterialTheme.shapes.large, colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                    Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        NeuroTag("ВСЕ ГОТОВО")
                        Text("Сегодня повторять нечего", style = MaterialTheme.typography.titleLarge)
                        Text("Пройдите следующую миссию: новые карточки появятся автоматически.")
                    }
                }
            }
            items(cards, key = { it.conceptId }) { card ->
                Card(Modifier.fillMaxWidth(), shape = MaterialTheme.shapes.large) {
                    Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        NeuroTag("ТЕРМИН")
                        Text(card.conceptId, style = MaterialTheme.typography.headlineSmall)
                        Text("Насколько уверенно вы можете объяснить это другому человеку?", color = MaterialTheme.colorScheme.onSurfaceVariant)
                        NeuroPrimaryButton(text = "Помню и могу объяснить", onClick = { viewModel.rate(card.conceptId, 5) })
                        NeuroSecondaryButton(text = "Нужно повторить", onClick = { viewModel.rate(card.conceptId, 2) })
                    }
                }
            }
        }
    }
}

@Composable private fun Summary(value: String, label: String, modifier: Modifier) {
    Card(modifier, shape = MaterialTheme.shapes.medium) { Column(Modifier.padding(14.dp)) { Text(value, style = MaterialTheme.typography.titleLarge, color = MaterialTheme.colorScheme.primary); Text(label, style = MaterialTheme.typography.bodySmall) } }
}
