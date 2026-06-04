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

package com.neuropoligon.presentation.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.domain.content.ContentEngine
import com.neuropoligon.domain.content.LearningMode
import com.neuropoligon.domain.content.Track
import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.domain.settings.SettingsRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public class HomeViewModel(
    contentEngine: ContentEngine,
    private val contentRepository: com.neuropoligon.domain.content.ContentRepository,
    private val settingsRepository: SettingsRepository,
    progressRepository: ProgressRepository,
) : ViewModel() {
    public val tracks: StateFlow<List<Track>> = contentEngine.observeFilteredTracks()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    public val primaryTrack: StateFlow<Track?> = tracks
        .combine(settingsRepository.observeLearningModeId()) { list, _ -> list.firstOrNull() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    public val learningModeId: StateFlow<String> = settingsRepository.observeLearningModeId()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), "standard_8_weeks")

    public val learningModes: StateFlow<List<LearningMode>> = primaryTrack
        .combine(learningModeId) { track, _ -> track?.learningModes.orEmpty() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    private val completedBlocks = progressRepository.observeCompleted().stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    public val streakDays: StateFlow<Int> = completedBlocks.map { blocks ->
        val days = blocks.map { it.completedAt / 86_400_000L }.distinct().sortedDescending()
        if (days.isEmpty()) 0 else { var streak = 1; var expected = days.first() - 1; for (day in days.drop(1)) { if (day == expected) { streak++; expected-- } else if (day < expected) break }; streak }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    public val progressFraction: StateFlow<Float> = combine(
        primaryTrack,
        completedBlocks,
    ) { track, completed ->
        val total = track?.modules?.size ?: 0
        if (total == 0) 0f
        else completed.map { it.moduleId }.distinct().count().toFloat() / total.toFloat()
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0f)

    init {
        viewModelScope.launch {
            contentRepository.getTracks()
            settingsRepository.getLearningModeId()
        }
    }

    public fun setLearningMode(modeId: String) {
        viewModelScope.launch { settingsRepository.setLearningModeId(modeId) }
    }

    public fun firstLessonModuleId(track: Track): String {
        val done = completedBlocks.value.map { it.moduleId }.toSet()
        return track.modules.firstOrNull { it.id !in done }?.id
            ?: track.modules.firstOrNull { it.id != "intro-course" }?.id
            ?: track.modules.firstOrNull()?.id
            ?: "intro-course"
    }
}
