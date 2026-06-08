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

package ru.nti.sbor.sync

import ru.nti.sbor.data.repository.LaborRepository
import ru.nti.sbor.data.settings.SecureServerSettings
import ru.nti.sbor.domain.model.SyncStatus
import ru.nti.sbor.sync.dto.BatchPushRequest
import ru.nti.sbor.sync.dto.LaborRecordDto
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.format.DateTimeFormatter

sealed class SyncResult {
    data object Success : SyncResult()
    data class Error(val message: String) : SyncResult()
    data object NotConfigured : SyncResult()
    data object NothingToSync : SyncResult()
}

sealed class HealthCheckResult {
    data object Ok : HealthCheckResult()
    data class Error(val message: String) : HealthCheckResult()
    data object NotConfigured : HealthCheckResult()
}

/** Синхронизация FR-013 — данные не теряются при ошибке. */
class SyncRepository(
    private val laborRepository: LaborRepository,
    private val secureSettings: SecureServerSettings,
) {
    private val dateFormatter = DateTimeFormatter.ISO_LOCAL_DATE

    suspend fun checkHealth(): HealthCheckResult = withContext(Dispatchers.IO) {
        val url = secureSettings.getServerUrl()
        if (url.isBlank()) return@withContext HealthCheckResult.NotConfigured
        try {
            NtiHttpClient(url).health()
            HealthCheckResult.Ok
        } catch (e: Exception) {
            HealthCheckResult.Error(e.message ?: "Ошибка соединения")
        }
    }

    suspend fun syncPending(): SyncResult = withContext(Dispatchers.IO) {
        val url = secureSettings.getServerUrl()
        val token = secureSettings.getAccessToken()
        if (url.isBlank() || token.isBlank()) return@withContext SyncResult.NotConfigured
        val pending = laborRepository.getPendingSyncRecords()
        if (pending.isEmpty()) return@withContext SyncResult.NothingToSync
        val auth = "Bearer $token"
        val dtoList = pending.map { record ->
            LaborRecordDto(
                clientId = record.clientId,
                date = dateFormatter.format(record.date),
                worker = record.worker,
                product = record.product,
                operation = record.operation,
                value = record.value,
                unit = record.unit.label,
                note = record.note,
            )
        }
        try {
            val response = NtiHttpClient(url).pushBatch(auth, BatchPushRequest(dtoList))
            val acceptedIds = response.accepted.map { it.clientId }.toSet()
            val syncedRecordIds = pending.filter { it.clientId in acceptedIds }.map { it.id }
            val errorIds = pending.filter { it.clientId !in acceptedIds }.map { it.id }
            if (syncedRecordIds.isNotEmpty()) {
                laborRepository.markSyncStatus(syncedRecordIds, SyncStatus.SYNCED)
            }
            if (errorIds.isNotEmpty()) {
                laborRepository.markSyncStatus(errorIds, SyncStatus.ERROR)
            }
            if (response.errors.isNotEmpty() && syncedRecordIds.isEmpty()) {
                SyncResult.Error(response.errors.first().message)
            } else {
                SyncResult.Success
            }
        } catch (e: Exception) {
            laborRepository.markSyncStatus(pending.map { it.id }, SyncStatus.ERROR)
            SyncResult.Error(e.message ?: "Ошибка синхронизации")
        }
    }

    suspend fun pullOperations(): Result<List<String>> = withContext(Dispatchers.IO) {
        val url = secureSettings.getServerUrl()
        val token = secureSettings.getAccessToken()
        if (url.isBlank() || token.isBlank()) {
            return@withContext Result.failure(IllegalStateException("Выполните вход на сервере"))
        }
        try {
            val ops = NtiHttpClient(url).operations("Bearer $token")
            Result.success(ops.filter { it.active }.map { it.name })
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
