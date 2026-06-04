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

package com.neuropoligon.data.content

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
internal data class AiIntroCourseSeedFile(
    @SerialName("courseId") val courseId: String,
    val title: String,
    val version: String = "1.0",
    val language: String = "ru",
    @SerialName("targetAudience") val targetAudience: List<String> = emptyList(),
    @SerialName("learningModes") val learningModes: List<SeedLearningMode> = emptyList(),
    val modules: List<SeedModule> = emptyList(),
    val resources: List<SeedResource> = emptyList(),
)

@Serializable
internal data class SeedLearningMode(
    val id: String,
    val title: String,
    val description: String,
)

@Serializable
internal data class SeedModule(
    val id: String,
    val order: Int,
    val title: String,
    val level: Int = 0,
    @SerialName("estimatedMinutes") val estimatedMinutes: Int = 45,
    val summary: String = "",
    val lessons: List<SeedLesson> = emptyList(),
)

@Serializable
internal data class SeedLesson(
    val id: String,
    val order: Int,
    val title: String,
    @SerialName("durationMinutes") val durationMinutes: Int = 12,
    @SerialName("contentRef") val contentRef: String = "",
    val practice: SeedPractice? = null,
    val quiz: List<SeedQuizQuestion> = emptyList(),
)

@Serializable
internal data class SeedPractice(
    val title: String,
    val prompt: String,
)

@Serializable
internal data class SeedQuizQuestion(
    val question: String,
    val options: List<String>,
    @SerialName("answerIndex") val answerIndex: Int,
    val explanation: String = "",
)

@Serializable
internal data class SeedResource(
    val title: String,
    val url: String,
    val level: Int = 0,
    val type: String = "guide",
)
