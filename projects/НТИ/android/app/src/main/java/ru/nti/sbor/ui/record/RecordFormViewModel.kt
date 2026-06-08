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

package ru.nti.sbor.ui.record

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import ru.nti.sbor.AppContainer
import ru.nti.sbor.domain.RecordFormInput
import ru.nti.sbor.domain.RecordValidator
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.util.DateFormats
import java.time.LocalDate

const val OTHER_OPERATION_LABEL = "Другая операция"

data class RecordFormUiState(
    val recordId: Long? = null,
    val operations: List<String> = emptyList(),
    val selectedOperation: String = "",
    val isOtherOperation: Boolean = false,
    val otherOperationText: String = "",
    val product: String = "",
    val valueText: String = "",
    val unit: LaborUnit = LaborUnit.NORM_HOUR,
    val dateText: String = DateFormats.format(LocalDate.now()),
    val worker: String = "",
    val note: String = "",
    val operationError: Boolean = false,
    val productError: Boolean = false,
    val valueError: Boolean = false,
    val workerError: Boolean = false,
    val otherOperationError: Boolean = false,
    val saved: Boolean = false,
    val isLoading: Boolean = true,
)

class RecordFormViewModel(
    private val container: AppContainer,
    private val editRecordId: Long?,
) : ViewModel() {
    private val _state = MutableStateFlow(RecordFormUiState())
    val state: StateFlow<RecordFormUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            val ops = container.laborRepository.observeOperations().first()
                .map { it.name }
                .filter { it != OTHER_OPERATION_LABEL }
            val profile = container.laborRepository.observeProfile().first()
            var initial = RecordFormUiState(
                operations = ops,
                selectedOperation = ops.firstOrNull() ?: "",
                worker = profile?.worker ?: "",
                isLoading = false,
            )
            editRecordId?.let { id ->
                container.laborRepository.getRecord(id)?.let { record ->
                    val isOther = record.operation !in ops
                    initial = initial.copy(
                        recordId = record.id,
                        selectedOperation = if (isOther) OTHER_OPERATION_LABEL else record.operation,
                        isOtherOperation = isOther,
                        otherOperationText = if (isOther) record.operation else "",
                        product = record.product,
                        valueText = record.value.toString().replace('.', ','),
                        unit = record.unit,
                        dateText = DateFormats.format(record.date),
                        worker = record.worker,
                        note = record.note,
                    )
                }
            }
            _state.value = initial
        }
    }

    fun update(block: (RecordFormUiState) -> RecordFormUiState) = _state.update(block)

    fun save() {
        val s = _state.value
        val input = RecordFormInput(
            operation = s.selectedOperation,
            product = s.product,
            valueText = s.valueText,
            unit = s.unit,
            date = DateFormats.parseOrToday(s.dateText),
            worker = s.worker,
            note = s.note,
            isOtherOperation = s.isOtherOperation,
            otherOperationText = s.otherOperationText,
        )
        val validation = RecordValidator.validate(input)
        if (!validation.isValid) {
            _state.update {
                it.copy(
                    operationError = validation.operationError,
                    productError = validation.productError,
                    valueError = validation.valueError,
                    workerError = validation.workerError,
                    otherOperationError = validation.otherOperationError,
                )
            }
            return
        }
        val value = RecordValidator.parseValue(s.valueText) ?: return
        val operationName = if (s.isOtherOperation) s.otherOperationText.trim() else s.selectedOperation
        viewModelScope.launch {
            if (s.recordId != null) {
                val existing = container.laborRepository.getRecord(s.recordId) ?: return@launch
                container.laborRepository.saveRecord(
                    existing.copy(
                        date = input.date,
                        worker = s.worker.trim(),
                        product = s.product.trim(),
                        operation = operationName,
                        value = value,
                        unit = s.unit,
                        note = s.note.trim(),
                        syncStatus = if (existing.syncStatus == SyncStatus.SYNCED) SyncStatus.LOCAL else existing.syncStatus,
                    ),
                )
            } else {
                container.laborRepository.createRecord(
                    date = input.date,
                    worker = s.worker.trim(),
                    product = s.product.trim(),
                    operation = operationName,
                    value = value,
                    unit = s.unit,
                    note = s.note.trim(),
                )
            }
            _state.update { it.copy(saved = true) }
        }
    }
}

class RecordFormViewModelFactory(
    private val container: AppContainer,
    private val editRecordId: Long?,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(RecordFormViewModel::class.java)) {
            return RecordFormViewModel(container, editRecordId) as T
        }
        throw IllegalArgumentException("Unknown ViewModel")
    }
}
