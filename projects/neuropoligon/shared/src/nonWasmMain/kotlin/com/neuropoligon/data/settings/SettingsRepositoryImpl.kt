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

import com.neuropoligon.data.progress.NeuropoligonDatabase
import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.domain.settings.LessonReaderSettings
import com.neuropoligon.domain.settings.SettingsRepository
import kotlinx.serialization.json.Json
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

public class SettingsRepositoryImpl(
    database: NeuropoligonDatabase,
) : SettingsRepository {
    private val queries = database.progressQueries
    private val levelFlow = MutableStateFlow(DifficultyLevel.Zero)
    private val learningModeFlow = MutableStateFlow(DEFAULT_LEARNING_MODE)
    private val readerFlow = MutableStateFlow(LessonReaderSettings())
    private val json = Json { ignoreUnknownKeys = true }

    override fun observeDifficultyLevel(): Flow<DifficultyLevel> = levelFlow.asStateFlow()

    override fun observeLearningModeId(): Flow<String> = learningModeFlow.asStateFlow()

    override suspend fun getDifficultyLevel(): DifficultyLevel {
        val raw = queries.selectPreference(PREF_LEVEL).executeAsOneOrNull()
        val level = raw?.let {
            runCatching { DifficultyLevel.valueOf(it) }.getOrDefault(DifficultyLevel.Zero)
        } ?: DifficultyLevel.Zero
        levelFlow.value = level
        return level
    }

    override suspend fun setDifficultyLevel(level: DifficultyLevel) {
        queries.upsertPreference(PREF_LEVEL, level.name)
        levelFlow.value = level
    }

    override suspend fun getLearningModeId(): String {
        val raw = queries.selectPreference(PREF_LEARNING_MODE).executeAsOneOrNull()
        val mode = raw?.takeIf { it.isNotBlank() } ?: DEFAULT_LEARNING_MODE
        learningModeFlow.value = mode
        return mode
    }

    override suspend fun setLearningModeId(modeId: String) {
        queries.upsertPreference(PREF_LEARNING_MODE, modeId)
        learningModeFlow.value = modeId
    }

    override suspend fun isOnboardingCompleted(): Boolean =
        queries.selectPreference(PREF_ONBOARDING).executeAsOneOrNull() == "true"

    override suspend fun setOnboardingCompleted(completed: Boolean) {
        queries.upsertPreference(PREF_ONBOARDING, completed.toString())
    }

    override fun observeLessonReaderSettings(): Flow<LessonReaderSettings> = readerFlow.asStateFlow()

    override suspend fun getLessonReaderSettings(): LessonReaderSettings {
        val raw = queries.selectPreference(PREF_READER).executeAsOneOrNull()
        val settings = raw?.let {
            runCatching { json.decodeFromString<LessonReaderSettings>(it) }.getOrNull()
        } ?: LessonReaderSettings()
        readerFlow.value = settings
        return settings
    }

    override suspend fun setLessonReaderSettings(settings: LessonReaderSettings) {
        queries.upsertPreference(PREF_READER, json.encodeToString(settings))
        readerFlow.value = settings
    }

    private companion object {
        private const val PREF_LEVEL = "difficulty_level"
        private const val PREF_LEARNING_MODE = "learning_mode_id"
        private const val PREF_ONBOARDING = "onboarding_done"
        private const val DEFAULT_LEARNING_MODE = "standard_8_weeks"
        private const val PREF_READER = "lesson_reader_settings"
    }
}
