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

package com.neuropoligon.domain.sandbox

import com.neuropoligon.domain.ai.AiError
import com.neuropoligon.domain.content.SandboxConfig
import com.neuropoligon.domain.content.SandboxType
import com.neuropoligon.foundations.Neighbor
import com.neuropoligon.foundations.Token
import com.neuropoligon.foundations.Vector

public data class SandboxUserInput(
    val text: String = "",
    val temperature: Double? = null,
    val topP: Double? = null,
    val systemPrompt: String? = null,
    val selectedProvider: String? = null,
)

public sealed class SandboxResult {
    public data class Tokenizer(val tokens: List<Token>) : SandboxResult()
    public data class Embedding(
        val word: String,
        val vector: Vector?,
        val neighbors: List<Neighbor>,
        val allPoints: List<Pair<String, Vector>>,
    ) : SandboxResult()
    public data class AiComparison(
        val prompt: String,
        val variants: List<AiVariant>,
        val degradationMessage: String? = null,
    ) : SandboxResult()
    public data class Rag(
        val chunks: List<ScoredChunk>,
        val answerWithContext: String?,
        val answerWithoutContext: String?,
        val degradationMessage: String? = null,
    ) : SandboxResult()
    public data class FunctionCalling(
        val steps: List<String>,
        val finalAnswer: String?,
        val degradationMessage: String? = null,
    ) : SandboxResult()
    public data class Agent(
        val steps: List<String>,
        val finalAnswer: String?,
        val degradationMessage: String? = null,
    ) : SandboxResult()
    public data class Error(val message: String) : SandboxResult()
}

public data class AiVariant(val label: String, val text: String)
public data class ScoredChunk(val text: String, val score: Double)
