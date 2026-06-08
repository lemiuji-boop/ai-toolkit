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

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.nti.sbor.domain.model.LaborUnit
import java.time.LocalDate

/** FR-003 */
class RecordValidatorTest {
    @Test
    fun validRecord_passes() {
        val result = RecordValidator.validate(
            RecordFormInput(
                operation = "Токарная",
                product = "Изделие-1",
                valueText = "1,5",
                unit = LaborUnit.NORM_HOUR,
                date = LocalDate.now(),
                worker = "Иванов И.И.",
            ),
        )
        assertTrue(result.isValid)
    }

    @Test
    fun zeroValue_fails() {
        val result = RecordValidator.validate(
            RecordFormInput(
                operation = "Токарная",
                product = "Изделие-1",
                valueText = "0",
                unit = LaborUnit.NORM_HOUR,
                date = LocalDate.now(),
                worker = "Иванов",
            ),
        )
        assertFalse(result.isValid)
        assertTrue(result.valueError)
    }

    @Test
    fun otherOperationEmpty_fails() {
        val result = RecordValidator.validate(
            RecordFormInput(
                operation = "Другая операция",
                product = "X",
                valueText = "2",
                unit = LaborUnit.MINUTE,
                date = LocalDate.now(),
                worker = "Иванов",
                isOtherOperation = true,
                otherOperationText = "",
            ),
        )
        assertFalse(result.isValid)
    }
}
