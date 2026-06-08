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

import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.domain.model.Operation
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.domain.model.WorkerProfile
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

fun RecordEntity.toDomain(): LaborRecord = LaborRecord(
    id = id,
    clientId = clientId,
    createdAtEpochMs = createdAtEpochMs,
    date = LocalDate.ofEpochDay(dateEpoch),
    worker = worker,
    product = product,
    operation = operation,
    value = value,
    unit = LaborUnit.entries.firstOrNull { it.name == unit } ?: LaborUnit.NORM_HOUR,
    note = note,
    syncStatus = SyncStatus.entries.firstOrNull { it.name == syncStatus } ?: SyncStatus.LOCAL,
)

fun LaborRecord.toEntity(): RecordEntity = RecordEntity(
    id = id,
    clientId = clientId,
    createdAtEpochMs = createdAtEpochMs,
    dateEpoch = date.toEpochDay(),
    worker = worker,
    product = product,
    operation = operation,
    value = value,
    unit = unit.name,
    note = note,
    syncStatus = syncStatus.name,
)

fun OperationEntity.toDomain(): Operation = Operation(id = id, name = name, active = active)

fun ProfileEntity.toDomain(): WorkerProfile = WorkerProfile(worker = worker, tabNumber = tabNumber)

fun WorkerProfile.toEntity(): ProfileEntity = ProfileEntity(worker = worker, tabNumber = tabNumber)

fun nowEpochMs(): Long = System.currentTimeMillis()

fun newClientId(): String = java.util.UUID.randomUUID().toString()
