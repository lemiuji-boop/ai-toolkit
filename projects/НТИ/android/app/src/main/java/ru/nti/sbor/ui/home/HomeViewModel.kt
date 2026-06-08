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

package ru.nti.sbor.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.flatMapLatest
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import ru.nti.sbor.AppContainer
import ru.nti.sbor.domain.LaborSummaryCalculator
import ru.nti.sbor.domain.model.LaborRecord
import java.util.Locale

data class HomeUiState(
    val records: List<LaborRecord> = emptyList(),
    val searchQuery: String = "",
    val summaryCount: Int = 0,
    val summaryTotal: String = "0",
    val summaryAverage: String = "0",
)

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModel(private val container: AppContainer) : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    init {
        viewModelScope.launch {
            if (!container.secureServerSettings.isLoggedIn()) return@launch
            container.syncRepository.pullOperations()
                .onSuccess { names -> container.laborRepository.replaceOperations(names) }
            container.syncRepository.syncPending()
        }
    }

    val uiState: StateFlow<HomeUiState> = searchQuery
        .flatMapLatest { query ->
            container.laborRepository.observeRecords(query).map { records ->
                val summary = LaborSummaryCalculator.calculate(records)
                HomeUiState(
                    records = records,
                    searchQuery = query,
                    summaryCount = summary.count,
                    summaryTotal = formatNum(summary.totalNormHours),
                    summaryAverage = formatNum(summary.averageNormHours),
                )
            }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), HomeUiState())

    fun onSearchChange(query: String) {
        searchQuery.value = query
    }

    fun deleteRecord(id: Long, onDone: () -> Unit) {
        viewModelScope.launch {
            container.laborRepository.deleteRecord(id)
            onDone()
        }
    }

    private fun formatNum(value: Double): String =
        String.format(Locale("ru"), "%.2f", value).replace('.', ',')
}

class HomeViewModelFactory(private val container: AppContainer) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(HomeViewModel::class.java)) {
            return HomeViewModel(container) as T
        }
        throw IllegalArgumentException("Unknown ViewModel")
    }
}
