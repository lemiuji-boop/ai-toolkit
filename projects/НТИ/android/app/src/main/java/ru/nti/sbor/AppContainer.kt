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

package ru.nti.sbor

import android.content.Context
import ru.nti.sbor.data.local.NtiDatabase
import ru.nti.sbor.data.repository.LaborRepository
import ru.nti.sbor.data.settings.AppPreferences
import ru.nti.sbor.data.settings.SecureServerSettings
import ru.nti.sbor.export.ExportShareManager
import ru.nti.sbor.auth.AuthRepository
import ru.nti.sbor.sync.SyncRepository

class AppContainer(context: Context) {
    private val appContext = context.applicationContext
    val database = NtiDatabase.get(appContext)
    val laborRepository = LaborRepository(database, appContext)
    val appPreferences = AppPreferences(appContext)
    val secureServerSettings = SecureServerSettings(appContext)
    val authRepository = AuthRepository(secureServerSettings, laborRepository)
    val syncRepository = SyncRepository(laborRepository, secureServerSettings)
    val exportShareManager = ExportShareManager(appContext)
}
