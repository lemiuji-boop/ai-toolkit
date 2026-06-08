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

package ru.nti.sbor.data.repository

import android.content.Context
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import ru.nti.sbor.data.local.NtiDatabase
import ru.nti.sbor.data.local.OperationSeedLoader
import ru.nti.sbor.data.local.newClientId
import ru.nti.sbor.data.local.nowEpochMs
import ru.nti.sbor.data.local.toDomain
import ru.nti.sbor.data.local.toEntity
import ru.nti.sbor.domain.model.LaborRecord
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.domain.model.Operation
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.domain.model.WorkerProfile
import java.time.LocalDate

class LaborRepository(
    private val database: NtiDatabase,
    private val appContext: Context,
) {
    private val recordDao = database.recordDao()
    private val operationDao = database.operationDao()
    private val profileDao = database.profileDao()

    fun observeRecords(query: String): Flow<List<LaborRecord>> {
        val flow = if (query.isBlank()) recordDao.observeAll() else recordDao.observeFiltered(query.trim())
        return flow.map { list -> list.map { it.toDomain() } }
    }

    fun observeOperations(): Flow<List<Operation>> =
        operationDao.observeActive().map { list -> list.map { it.toDomain() } }

    fun observeProfile(): Flow<WorkerProfile?> =
        profileDao.observeProfile().map { it?.toDomain() }

    suspend fun getRecord(id: Long): LaborRecord? = recordDao.getById(id)?.toDomain()

    suspend fun saveRecord(record: LaborRecord): Long {
        val entity = record.toEntity()
        return if (entity.id == 0L) {
            recordDao.insert(entity)
        } else {
            recordDao.update(entity)
            entity.id
        }
    }

    suspend fun createRecord(
        date: LocalDate,
        worker: String,
        product: String,
        operation: String,
        value: Double,
        unit: LaborUnit,
        note: String,
    ): Long {
        val record = LaborRecord(
            clientId = newClientId(),
            createdAtEpochMs = nowEpochMs(),
            date = date,
            worker = worker,
            product = product,
            operation = operation,
            value = value,
            unit = unit,
            note = note,
            syncStatus = SyncStatus.LOCAL,
        )
        return saveRecord(record)
    }

    suspend fun deleteRecord(id: Long) = recordDao.deleteById(id)

    suspend fun saveProfile(profile: WorkerProfile) = profileDao.upsert(profile.toEntity())

    suspend fun replaceOperations(names: List<String>) {
        operationDao.deleteAll()
        operationDao.insertAll(
            names.distinct().map { name ->
                ru.nti.sbor.data.local.OperationEntity(name = name, active = true)
            },
        )
    }

    suspend fun clearAllData() {
        recordDao.deleteAll()
        profileDao.deleteAll()
        operationDao.deleteAll()
        OperationSeedLoader.seedIfEmpty(operationDao, appContext)
    }

    suspend fun getPendingSyncRecords(): List<LaborRecord> =
        recordDao.getPendingSync().map { it.toDomain() }

    suspend fun markSyncStatus(ids: List<Long>, status: SyncStatus) {
        recordDao.updateSyncStatus(ids, status.name)
    }
}
