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

package ru.nti.sbor.data.local

import android.content.Context
import java.io.BufferedReader
import java.io.InputStreamReader

/** Загрузка встроенного справочника операций из assets. */
object OperationSeedLoader {
    suspend fun seedIfEmpty(dao: OperationDao, context: Context) {
        if (dao.getAll().isNotEmpty()) return
        val names = loadDefaultNames(context)
        dao.insertAll(names.map { OperationEntity(name = it, active = true) })
    }

    fun loadDefaultNames(context: Context): List<String> {
        context.assets.open("operations_default.csv").use { stream ->
            BufferedReader(InputStreamReader(stream, Charsets.UTF_8)).use { reader ->
                return reader.lineSequence()
                    .drop(1)
                    .map { it.trim() }
                    .filter { it.isNotEmpty() }
                    .toList()
            }
        }
    }
}
