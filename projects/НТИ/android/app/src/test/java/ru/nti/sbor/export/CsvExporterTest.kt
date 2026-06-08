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

package ru.nti.sbor.export

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.domain.model.SyncStatus
import java.time.LocalDate

/** FR-008 */
class CsvExporterTest {
    @Test
    fun export_hasBomAndSemicolon() {
        val bytes = CsvExporter.export(
            listOf(
                LaborRecord(
                    id = 1,
                    clientId = "uuid-1",
                    createdAtEpochMs = 0,
                    date = LocalDate.of(2026, 6, 4),
                    worker = "Петров",
                    product = "З-100",
                    operation = "Токарная",
                    value = 1.25,
                    unit = LaborUnit.NORM_HOUR,
                    note = "тест",
                    syncStatus = SyncStatus.LOCAL,
                ),
            ),
        )
        val text = String(bytes, Charsets.UTF_8)
        assertTrue(text.startsWith("\uFEFF"))
        assertTrue(text.contains(";"))
        assertTrue(text.contains("Петров"))
        assertTrue(text.contains("Токарная"))
    }

    @Test
    fun parseOperationsCsv_valid() {
        val result = CsvExporter.parseOperationsCsv("name\nОп1\nОп2")
        assertTrue(result.isSuccess)
        assertEquals(listOf("Оп1", "Оп2"), result.getOrNull())
    }
}
