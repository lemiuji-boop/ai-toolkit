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

package ru.nti.sbor.domain.model

import java.time.LocalDate

/** Доменная модель записи трудоёмкости. */
data class LaborRecord(
    val id: Long = 0L,
    val clientId: String,
    val createdAtEpochMs: Long,
    val date: LocalDate,
    val worker: String,
    val product: String,
    val operation: String,
    val value: Double,
    val unit: LaborUnit,
    val note: String,
    val syncStatus: SyncStatus,
)
