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

import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.LaborUnit
import java.time.format.DateTimeFormatter

/** Экспорт FR-008: UTF-8 BOM, разделитель ';'. */
object CsvExporter {
    private val dateFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy")
    private const val BOM = "\uFEFF"

    private val header = listOf(
        "id",
        "client_id",
        "дата",
        "исполнитель",
        "изделие",
        "операция",
        "значение",
        "единица",
        "примечание",
        "статус_синхронизации",
    )

    fun export(records: List<LaborRecord>): ByteArray {
        val lines = buildList {
            add(header.joinToString(";"))
            records.forEach { record ->
                add(
                    listOf(
                        record.id.toString(),
                        record.clientId,
                        dateFormatter.format(record.date),
                        escape(record.worker),
                        escape(record.product),
                        escape(record.operation),
                        formatValue(record.value),
                        record.unit.label,
                        escape(record.note),
                        record.syncStatus.name,
                    ).joinToString(";"),
                )
            }
        }
        val body = lines.joinToString("\r\n")
        return (BOM + body).toByteArray(Charsets.UTF_8)
    }

    private fun formatValue(value: Double): String =
        value.toString().replace('.', ',')

    private fun escape(value: String): String {
        if (value.contains(';') || value.contains('"') || value.contains('\n')) {
            return "\"${value.replace("\"", "\"\"")}\""
        }
        return value
    }

    fun parseOperationsCsv(content: String): Result<List<String>> {
        val lines = content.trim().lines()
        if (lines.isEmpty()) return Result.failure(IllegalArgumentException("Пустой файл"))
        val startIndex = if (lines.first().lowercase().contains("name") ||
            lines.first().lowercase().contains("операц")
        ) {
            1
        } else {
            0
        }
        val names = lines.drop(startIndex).map { it.trim() }.filter { it.isNotEmpty() }
        if (names.isEmpty()) return Result.failure(IllegalArgumentException("Нет операций в файле"))
        return Result.success(names)
    }
}
