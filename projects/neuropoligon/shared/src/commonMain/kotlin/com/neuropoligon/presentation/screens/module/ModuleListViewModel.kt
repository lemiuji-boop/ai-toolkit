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

package com.neuropoligon.presentation.screens.module

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.domain.content.ContentEngine
import com.neuropoligon.domain.content.Track
import com.neuropoligon.domain.progress.ProgressRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public class ModuleListViewModel(
    private val contentEngine: ContentEngine,
    progressRepository: ProgressRepository,
) : ViewModel() {
    private val trackIdFlow = MutableStateFlow("")
    private val _track = MutableStateFlow<Track?>(null)
    public val track: StateFlow<Track?> = _track.asStateFlow()

    public val completedModuleIds: StateFlow<Set<String>> = progressRepository.observeCompleted()
        .map { list -> list.filter { it.trackId == trackIdFlow.value }.map { it.moduleId }.toSet() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptySet())

    public fun load(trackId: String) {
        trackIdFlow.value = trackId
        viewModelScope.launch {
            contentEngine.observeFilteredTracks().collect { tracks ->
                _track.value = tracks.firstOrNull { it.id == trackId }
            }
        }
    }
}
