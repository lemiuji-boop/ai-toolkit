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
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.selection.selectable
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.Block
import com.neuropoligon.domain.content.QuizQuestion

@Composable
public fun QuizBlockView(
    block: Block.Quiz,
    onCompleted: () -> Unit = {},
) {
    val answers = remember { mutableStateMapOf<Int, Int>() }
    var checked by remember { mutableStateOf(false) }
    var score by remember { mutableStateOf(0) }

    Column(Modifier.fillMaxWidth().padding(top = 4.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
        block.questions.forEachIndexed { index, question ->
            QuizQuestionView(
                index = index,
                question = question,
                selected = answers[index],
                showResult = checked,
                onSelect = { optionIndex -> answers[index] = optionIndex },
            )
        }
        Button(
            onClick = {
                checked = true
                score = block.questions.indices.count { i ->
                    answers[i] == block.questions[i].answerIndex
                }
                if (score == block.questions.size) onCompleted()
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = block.questions.indices.all { answers.containsKey(it) },
        ) {
            Text(if (checked) "Проверено" else "Проверить ответы")
        }
        if (checked) {
            Text(
                "Результат: $score из ${block.questions.size}",
                color = if (score == block.questions.size) {
                    Color(0xFF059669)
                } else {
                    MaterialTheme.colorScheme.error
                },
            )
        }
    }
}

@Composable
private fun QuizQuestionView(
    index: Int,
    question: QuizQuestion,
    selected: Int?,
    showResult: Boolean,
    onSelect: (Int) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            "${index + 1}. ${question.question}",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface,
        )
        question.options.forEachIndexed { optionIndex, option ->
            val isSelected = selected == optionIndex
            val isCorrect = optionIndex == question.answerIndex
            val rowColor = when {
                !showResult -> MaterialTheme.colorScheme.surface
                isCorrect -> MaterialTheme.colorScheme.tertiaryContainer
                isSelected && !isCorrect -> MaterialTheme.colorScheme.errorContainer
                else -> MaterialTheme.colorScheme.surface
            }
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .selectable(
                        selected = isSelected,
                        onClick = { if (!showResult) onSelect(optionIndex) },
                    ),
                colors = CardDefaults.cardColors(
                    containerColor = rowColor,
                    contentColor = MaterialTheme.colorScheme.onSurface,
                ),
            ) {
                Row(Modifier.padding(8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    RadioButton(selected = isSelected, onClick = null)
                    Text(option, modifier = Modifier.weight(1f), color = MaterialTheme.colorScheme.onSurface)
                }
            }
        }
        if (showResult && selected != null && selected != question.answerIndex) {
            Text(
                question.explanation,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}
