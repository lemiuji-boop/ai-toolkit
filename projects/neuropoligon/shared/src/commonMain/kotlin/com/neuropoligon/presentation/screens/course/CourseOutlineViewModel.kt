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

package com.neuropoligon.presentation.screens.course

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.domain.content.ContentEngine
import com.neuropoligon.domain.content.ContentRepository
import com.neuropoligon.domain.content.Module
import com.neuropoligon.domain.content.Track
import com.neuropoligon.domain.progress.ProgressRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public data class CourseChapter(
    val id: String,
    val title: String,
    val lessons: List<Module>,
)

public class CourseOutlineViewModel(
    contentRepository: ContentRepository,
    contentEngine: ContentEngine,
    progressRepository: ProgressRepository,
) : ViewModel() {
    init {
        viewModelScope.launch { contentRepository.getTracks() }
    }
    public val track: StateFlow<Track?> = contentEngine.observeFilteredTracks()
        .map { it.firstOrNull() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    public val chapters: StateFlow<List<CourseChapter>> = track
        .map { current ->
            current?.modules
                ?.filter { it.id != "intro-course" }
                ?.groupBy { it.chapterId ?: "other" }
                ?.map { (id, lessons) ->
                    CourseChapter(
                        id = id,
                        title = lessons.firstOrNull()?.chapterTitle ?: "Раздел",
                        lessons = lessons.sortedBy { it.lessonOrder ?: 0 },
                    )
                }
                ?.sortedBy { chapter -> chapter.lessons.firstOrNull()?.chapterOrder ?: 0 }
                ?: emptyList()
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    public val completedModuleIds: StateFlow<Set<String>> = progressRepository.observeCompleted()
        .map { list -> list.map { it.moduleId }.toSet() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptySet())
}
