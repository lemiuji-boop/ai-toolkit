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

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface RecordDao {
    @Query("SELECT * FROM labor_records ORDER BY dateEpoch DESC, createdAtEpochMs DESC")
    fun observeAll(): Flow<List<RecordEntity>>

    @Query(
        """
        SELECT * FROM labor_records
        WHERE worker LIKE '%' || :query || '%'
           OR product LIKE '%' || :query || '%'
           OR operation LIKE '%' || :query || '%'
        ORDER BY dateEpoch DESC, createdAtEpochMs DESC
        """,
    )
    fun observeFiltered(query: String): Flow<List<RecordEntity>>

    @Query("SELECT * FROM labor_records WHERE id = :id LIMIT 1")
    suspend fun getById(id: Long): RecordEntity?

    @Query("SELECT * FROM labor_records WHERE syncStatus != 'SYNCED'")
    suspend fun getPendingSync(): List<RecordEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entity: RecordEntity): Long

    @Update
    suspend fun update(entity: RecordEntity)

    @Query("DELETE FROM labor_records WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("DELETE FROM labor_records")
    suspend fun deleteAll()

    @Query("UPDATE labor_records SET syncStatus = :status WHERE id IN (:ids)")
    suspend fun updateSyncStatus(ids: List<Long>, status: String)
}

@Dao
interface OperationDao {
    @Query("SELECT * FROM operations WHERE active = 1 ORDER BY name ASC")
    fun observeActive(): Flow<List<OperationEntity>>

    @Query("SELECT * FROM operations ORDER BY name ASC")
    suspend fun getAll(): List<OperationEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(entities: List<OperationEntity>)

    @Query("DELETE FROM operations")
    suspend fun deleteAll()
}

@Dao
interface ProfileDao {
    @Query("SELECT * FROM profile WHERE id = 1 LIMIT 1")
    fun observeProfile(): Flow<ProfileEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(entity: ProfileEntity)

    @Query("DELETE FROM profile")
    suspend fun deleteAll()
}
