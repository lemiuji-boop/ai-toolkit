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

package ru.nti.sbor.domain

import ru.nti.sbor.domain.model.LaborUnit
import java.time.LocalDate

/** Валидация FR-003. */
data class RecordFormInput(
    val operation: String,
    val product: String,
    val valueText: String,
    val unit: LaborUnit,
    val date: LocalDate,
    val worker: String,
    val note: String = "",
    val isOtherOperation: Boolean = false,
    val otherOperationText: String = "",
)

data class ValidationResult(
    val isValid: Boolean,
    val operationError: Boolean = false,
    val productError: Boolean = false,
    val valueError: Boolean = false,
    val workerError: Boolean = false,
    val otherOperationError: Boolean = false,
)

object RecordValidator {
    fun validate(input: RecordFormInput): ValidationResult {
        val operationName = if (input.isOtherOperation) {
            input.otherOperationText.trim()
        } else {
            input.operation.trim()
        }
        val value = parseValue(input.valueText)
        val operationError = operationName.isEmpty() ||
            (input.isOtherOperation && input.otherOperationText.trim().isEmpty())
        val productError = input.product.trim().isEmpty()
        val valueError = value == null || value <= 0.0
        val workerError = input.worker.trim().isEmpty()
        val isValid = !operationError && !productError && !valueError && !workerError
        return ValidationResult(
            isValid = isValid,
            operationError = operationError,
            productError = productError,
            valueError = valueError,
            workerError = workerError,
            otherOperationError = input.isOtherOperation && input.otherOperationText.trim().isEmpty(),
        )
    }

    /** Парсинг числа с запятой как десятичным разделителем (NFR-007). */
    fun parseValue(text: String): Double? {
        val normalized = text.trim().replace(" ", "").replace(',', '.')
        if (normalized.isEmpty()) return null
        return normalized.toDoubleOrNull()
    }
}
