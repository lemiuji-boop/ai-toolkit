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

package com.neuropoligon.domain.settings

import com.neuropoligon.domain.content.DifficultyLevel
import kotlinx.coroutines.flow.Flow

public interface SettingsRepository {
    public fun observeDifficultyLevel(): Flow<DifficultyLevel>
    public suspend fun getDifficultyLevel(): DifficultyLevel
    public suspend fun setDifficultyLevel(level: DifficultyLevel)
    public fun observeLearningModeId(): Flow<String>
    public suspend fun getLearningModeId(): String
    public suspend fun setLearningModeId(modeId: String)
    public suspend fun isOnboardingCompleted(): Boolean
    public suspend fun setOnboardingCompleted(completed: Boolean)
    public fun observeLessonReaderSettings(): Flow<LessonReaderSettings>
    public suspend fun getLessonReaderSettings(): LessonReaderSettings
    public suspend fun setLessonReaderSettings(settings: LessonReaderSettings)
}
