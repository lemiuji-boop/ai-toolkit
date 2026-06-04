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

package com.neuropoligon.domain.content

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
public data class Track(
    val id: String,
    val title: String,
    val description: String,
    val modules: List<Module> = emptyList(),
    @SerialName("requiresApiKey") val requiresApiKey: Boolean = false,
    @SerialName("minLevel") val minLevel: DifficultyLevel = DifficultyLevel.Zero,
    @SerialName("learningModes") val learningModes: List<LearningMode> = emptyList(),
    @SerialName("targetAudience") val targetAudience: List<String> = emptyList(),
)

@Serializable
public data class Module(
    val id: String,
    val title: String,
    val blocks: List<Block> = emptyList(),
    @SerialName("minLevel") val minLevel: DifficultyLevel = DifficultyLevel.Zero,
    val summary: String? = null,
    @SerialName("chapterId") val chapterId: String? = null,
    @SerialName("chapterTitle") val chapterTitle: String? = null,
    @SerialName("chapterOrder") val chapterOrder: Int? = null,
    @SerialName("lessonOrder") val lessonOrder: Int? = null,
    @SerialName("durationMinutes") val durationMinutes: Int? = null,
)

@Serializable
public sealed class Block {
    @Serializable
    @SerialName("explanation")
    public data class Explanation(
        val markdownByLevel: Map<DifficultyLevel, String> = emptyMap(),
        val markdown: String? = null,
        @SerialName("advancedOnly") val advancedOnly: Boolean = false,
        @SerialName("coreForAll") val coreForAll: Boolean = true,
    ) : Block()

    @Serializable
    @SerialName("sandbox")
    public data class Sandbox(
        @SerialName("sandboxType") val sandboxType: SandboxType,
        val config: SandboxConfig = SandboxConfig(),
        @SerialName("advancedOnly") val advancedOnly: Boolean = false,
    ) : Block()

    @Serializable
    @SerialName("challenge")
    public data class ChallengeBlock(
        val challenge: Challenge,
    ) : Block()

    @Serializable
    @SerialName("codeRecipe")
    public data class CodeRecipe(
        val language: CodeLang,
        val code: String,
        val note: String = "",
    ) : Block()

    @Serializable
    @SerialName("practice")
    public data class Practice(
        val title: String,
        val prompt: String,
    ) : Block()

    @Serializable
    @SerialName("quiz")
    public data class Quiz(
        val questions: List<QuizQuestion> = emptyList(),
    ) : Block()
}

@Serializable
public data class QuizQuestion(
    val question: String,
    val options: List<String>,
    @SerialName("answerIndex") val answerIndex: Int,
    val explanation: String = "",
)

@Serializable
public data class LearningMode(
    val id: String,
    val title: String,
    val description: String,
)

@Serializable
public enum class SandboxType {
    @SerialName("tokenizer")
    Tokenizer,

    @SerialName("embedding")
    Embedding,

    @SerialName("temperature")
    Temperature,

    @SerialName("topP")
    TopP,

    @SerialName("systemPrompt")
    SystemPrompt,

    @SerialName("rag")
    Rag,

    @SerialName("functionCalling")
    FunctionCalling,

    @SerialName("agent")
    Agent,
}

@Serializable
public data class SandboxConfig(
    val prompt: String = "",
    val documents: List<String> = emptyList(),
    val defaultTemperature: Double = 0.7,
    val defaultTopP: Double = 0.9,
)

@Serializable
public enum class CodeLang {
    @SerialName("kotlin")
    Kotlin,

    @SerialName("javascript")
    JavaScript,

    @SerialName("python")
    Python,
}

@Serializable
public data class Challenge(
    val id: String,
    val title: String,
    val description: String,
    val criterion: ChallengeCriterion,
)

@Serializable
public sealed class ChallengeCriterion {
    @Serializable
    @SerialName("sandboxParam")
    public data class SandboxParam(
        @SerialName("paramName") val paramName: String,
        val operator: String,
        val value: Double,
    ) : ChallengeCriterion()

    @Serializable
    @SerialName("responseContains")
    public data class ResponseContains(
        val substring: String,
    ) : ChallengeCriterion()
}

@Serializable
public data class GlossaryEntry(
    val id: String,
    val term: String,
    val aliases: List<String> = emptyList(),
    @SerialName("naiveDefinition") val naiveDefinition: String,
    @SerialName("fullDefinition") val fullDefinition: String? = null,
    @SerialName("relatedIds") val relatedIds: List<String> = emptyList(),
)

@Serializable
public data class ResourceEntry(
    val id: String,
    val name: String,
    val category: String,
    @SerialName("whatItIs") val whatItIs: String,
    @SerialName("useFor") val useFor: String,
    @SerialName("officialUrl") val officialUrl: String,
    @SerialName("docsUrl") val docsUrl: String? = null,
)

@Serializable
public data class TracksFile(val tracks: List<Track> = emptyList())

@Serializable
public data class GlossaryFile(val entries: List<GlossaryEntry> = emptyList())

@Serializable
public data class ResourcesFile(val resources: List<ResourceEntry> = emptyList())
