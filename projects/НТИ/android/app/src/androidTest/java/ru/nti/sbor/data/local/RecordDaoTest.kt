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
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

/** FR-004, FR-005 */
@RunWith(AndroidJUnit4::class)
class RecordDaoTest {
    private lateinit var db: NtiDatabase

    @Before
    fun setup() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        db = Room.inMemoryDatabaseBuilder(context, NtiDatabase::class.java).build()
    }

    @After
    fun tearDown() {
        db.close()
    }

    @Test
    fun insertAndObserve_sortedByDateDesc() = runBlocking {
        val dao = db.recordDao()
        dao.insert(
            RecordEntity(
                clientId = "a",
                createdAtEpochMs = 1,
                dateEpoch = 100,
                worker = "W",
                product = "P",
                operation = "O",
                value = 1.0,
                unit = "NORM_HOUR",
                note = "",
                syncStatus = "LOCAL",
            ),
        )
        dao.insert(
            RecordEntity(
                clientId = "b",
                createdAtEpochMs = 2,
                dateEpoch = 200,
                worker = "W",
                product = "P",
                operation = "O",
                value = 2.0,
                unit = "NORM_HOUR",
                note = "",
                syncStatus = "LOCAL",
            ),
        )
        val list = dao.observeAll().first()
        assertEquals(200, list.first().dateEpoch)
    }
}
