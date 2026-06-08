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

import org.junit.Assert.assertEquals
import org.junit.Test
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.domain.model.SyncStatus
import java.time.LocalDate

class LaborSummaryTest {
    @Test
    fun summary_mixedUnits() {
        val records = listOf(
            record(1.0, LaborUnit.NORM_HOUR),
            record(30.0, LaborUnit.MINUTE),
        )
        val summary = LaborSummaryCalculator.calculate(records)
        assertEquals(2, summary.count)
        assertEquals(1.5, summary.totalNormHours, 0.001)
        assertEquals(0.75, summary.averageNormHours, 0.001)
    }

    private fun record(value: Double, unit: LaborUnit) = LaborRecord(
        clientId = "c1",
        createdAtEpochMs = 0,
        date = LocalDate.now(),
        worker = "W",
        product = "P",
        operation = "O",
        value = value,
        unit = unit,
        note = "",
        syncStatus = SyncStatus.LOCAL,
    )
}
