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

package com.neuropoligon.presentation.sandbox

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.sandbox.SandboxResult

@Composable
public fun SandboxResultView(result: SandboxResult) {
    when (result) {
        is SandboxResult.Tokenizer -> {
            Text("Токены: ${result.tokens.joinToString(" | ") { "[${it.text}]" }}")
        }
        is SandboxResult.Embedding -> {
            Text("Слово: ${result.word}")
            Text(
                "Соседи: ${result.neighbors.joinToString { "${it.word} (${it.distance.toFixed(2)})" }}",
            )
            Canvas(Modifier.fillMaxWidth().height(200.dp)) {
                val points = result.allPoints
                if (points.isEmpty()) return@Canvas
                val maxX = points.maxOf { it.second.x }
                val maxY = points.maxOf { it.second.y }
                points.forEach { (word, vector) ->
                    val x = (vector.x / maxX.coerceAtLeast(0.01) * size.width).toFloat()
                    val y = (vector.y / maxY.coerceAtLeast(0.01) * size.height).toFloat()
                    drawCircle(Color.Blue, 6f, Offset(x, y))
                }
            }
        }
        is SandboxResult.AiComparison -> {
            result.degradationMessage?.let { Text(it) }
            result.variants.forEach { Text("${it.label}: ${it.text}") }
        }
        is SandboxResult.Rag -> {
            Text("Чанки:")
            result.chunks.forEach { Text("- ${it.text} (${it.score})") }
            result.answerWithContext?.let { Text("С контекстом: $it") }
            result.answerWithoutContext?.let { Text("Без контекста: $it") }
            result.degradationMessage?.let { Text(it) }
        }
        is SandboxResult.FunctionCalling -> {
            result.steps.forEach { Text(it) }
            result.finalAnswer?.let { Text(it) }
            result.degradationMessage?.let { Text(it) }
        }
        is SandboxResult.Agent -> {
            result.steps.forEach { Text(it) }
            result.finalAnswer?.let { Text(it) }
            result.degradationMessage?.let { Text(it) }
        }
        is SandboxResult.Error -> Text(result.message)
    }
}

private fun Double.toFixed(digits: Int): String {
    var factor = 1.0
    repeat(digits) { factor *= 10.0 }
    val rounded = kotlin.math.round(this * factor) / factor
    return rounded.toString()
}
