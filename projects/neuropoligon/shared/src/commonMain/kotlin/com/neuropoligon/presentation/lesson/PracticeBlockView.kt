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

package com.neuropoligon.presentation.lesson

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.Block
import com.neuropoligon.platform.copyToClipboard

@Composable
public fun PracticeBlockView(
    block: Block.Practice,
    onCopied: (String) -> Unit = {},
) {
    var draft by remember(block.prompt) { mutableStateOf(block.prompt) }
    Column(
        Modifier.fillMaxWidth().padding(top = 4.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            "Скопируйте промт в ChatGPT, Claude или Gemini и выполните задание на своём примере.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        OutlinedTextField(
            value = draft,
            onValueChange = { draft = it },
            modifier = Modifier.fillMaxWidth(),
            label = { Text(block.title) },
            minLines = 5,
        )
        Button(
            onClick = {
                copyToClipboard(draft)
                onCopied("Промт скопирован в буфер обмена")
            },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Скопировать промт")
        }
        TextButton(onClick = { draft = block.prompt }) {
            Text("Сбросить к шаблону")
        }
    }
}
