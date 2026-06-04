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

package com.neuropoligon.data.settings

import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.domain.settings.LessonReaderSettings
import com.neuropoligon.domain.settings.SettingsRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

public class InMemorySettingsRepository : SettingsRepository {
    private val levelFlow = MutableStateFlow(DifficultyLevel.Zero)
    private val learningModeFlow = MutableStateFlow("standard_8_weeks")
    private var onboardingDone: Boolean = false
    private val readerFlow = MutableStateFlow(LessonReaderSettings())

    override fun observeDifficultyLevel(): Flow<DifficultyLevel> = levelFlow.asStateFlow()

    override fun observeLearningModeId(): Flow<String> = learningModeFlow.asStateFlow()

    override suspend fun getDifficultyLevel(): DifficultyLevel = levelFlow.value

    override suspend fun setDifficultyLevel(level: DifficultyLevel) {
        levelFlow.value = level
    }

    override suspend fun getLearningModeId(): String = learningModeFlow.value

    override suspend fun setLearningModeId(modeId: String) {
        learningModeFlow.value = modeId
    }

    override suspend fun isOnboardingCompleted(): Boolean = onboardingDone

    override suspend fun setOnboardingCompleted(completed: Boolean) {
        onboardingDone = completed
    }

    override fun observeLessonReaderSettings(): Flow<LessonReaderSettings> = readerFlow.asStateFlow()

    override suspend fun getLessonReaderSettings(): LessonReaderSettings = readerFlow.value

    override suspend fun setLessonReaderSettings(settings: LessonReaderSettings) {
        readerFlow.value = settings
    }
}
