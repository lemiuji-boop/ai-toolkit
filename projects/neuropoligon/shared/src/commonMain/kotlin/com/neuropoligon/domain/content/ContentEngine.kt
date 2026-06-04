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

import com.neuropoligon.domain.settings.SettingsRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine

/**
 * Фильтрация и подстановка контента по уровню сложности.
 */
public class ContentEngine(
    private val contentRepository: ContentRepository,
    private val settingsRepository: SettingsRepository,
) {
    public fun observeFilteredTracks(): Flow<List<Track>> =
        combine(
            contentRepository.observeTracks(),
            settingsRepository.observeDifficultyLevel(),
            settingsRepository.observeLearningModeId(),
        ) { tracks, level, learningModeId ->
            tracks.mapNotNull { track -> filterTrack(track, level, learningModeId) }
        }

    public fun resolveMarkdown(block: Block.Explanation, level: DifficultyLevel): String {
        val byLevel = block.markdownByLevel
        if (byLevel.isNotEmpty()) {
            return byLevel[level]
                ?: byLevel[DifficultyLevel.Zero]
                ?: byLevel.values.firstOrNull()
                ?: ""
        }
        return block.markdown.orEmpty()
    }

    public fun isBlockVisible(block: Block, level: DifficultyLevel): Boolean = when (block) {
        is Block.Explanation -> {
            if (block.advancedOnly && level.order() < DifficultyLevel.Intermediate.order()) false
            else true
        }
        is Block.Sandbox -> {
            if (block.advancedOnly && level.order() < DifficultyLevel.Intermediate.order()) false
            else true
        }
        else -> true
    }

    private fun filterTrack(track: Track, level: DifficultyLevel, learningModeId: String): Track? {
        if (track.minLevel.order() > level.order() && level != DifficultyLevel.Advanced) {
            return null
        }
        var modules = track.modules
            .filter { module -> module.minLevel.order() <= level.order() || level == DifficultyLevel.Advanced }
            .map { module ->
                module.copy(
                    blocks = module.blocks.filter { isBlockVisible(it, level) },
                )
            }
        modules = filterModulesByLearningMode(modules, learningModeId)
        if (modules.isEmpty()) return null
        return track.copy(modules = modules)
    }

    private fun filterModulesByLearningMode(modules: List<Module>, learningModeId: String): List<Module> {
        val intro = modules.firstOrNull { it.id == "intro-course" }
        val lessons = modules.filter { it.id != "intro-course" }
        val filteredLessons = when (learningModeId) {
            "quick_7_days" -> lessons.take(49)
            "deep_12_weeks" -> lessons
            else -> lessons.filter { module ->
                module.minLevel.order() <= DifficultyLevel.Intermediate.order()
            }
        }
        return listOfNotNull(intro) + filteredLessons
    }
}
