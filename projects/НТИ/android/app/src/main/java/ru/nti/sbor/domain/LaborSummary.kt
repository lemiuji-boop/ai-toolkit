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

import ru.nti.sbor.domain.model.LaborRecord

/** Сводка FR-011. */
data class LaborSummary(
    val count: Int,
    val totalNormHours: Double,
    val averageNormHours: Double,
)

object LaborSummaryCalculator {
    fun calculate(records: List<LaborRecord>): LaborSummary {
        if (records.isEmpty()) {
            return LaborSummary(count = 0, totalNormHours = 0.0, averageNormHours = 0.0)
        }
        val total = records.sumOf { UnitConverter.toNormHours(it.value, it.unit) }
        return LaborSummary(
            count = records.size,
            totalNormHours = total,
            averageNormHours = total / records.size,
        )
    }
}
