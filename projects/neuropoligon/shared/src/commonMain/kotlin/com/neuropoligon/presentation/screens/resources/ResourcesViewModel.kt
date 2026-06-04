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

package com.neuropoligon.presentation.screens.resources

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.domain.content.ResourceEntry
import com.neuropoligon.domain.content.ResourcesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.launch

public class ResourcesViewModel(private val repository: ResourcesRepository) : ViewModel() {
    private val all = MutableStateFlow<List<ResourceEntry>>(emptyList())
    private val _query = MutableStateFlow("")
    public val query: StateFlow<String> = _query.asStateFlow()
    public val resources: StateFlow<List<ResourceEntry>> = combine(all, query) { entries, q ->
        if (q.isBlank()) entries else entries.filter {
            listOf(it.name, it.category, it.whatItIs, it.useFor).any { value -> value.contains(q, ignoreCase = true) }
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init { viewModelScope.launch { all.value = repository.getResources() } }
    public fun search(value: String) { _query.value = value }
}
