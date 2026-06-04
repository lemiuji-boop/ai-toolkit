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

package com.neuropoligon.data.notifications

import com.neuropoligon.domain.notifications.AuthEmailEvent
import com.neuropoligon.domain.notifications.AuthEmailNotifier

/**
 * Сначала пробует отправить в backend webhook, затем использует fallback через FormSubmit.
 */
public class CompositeAuthEmailNotifier(
    private val backendNotifier: BackendAuthEmailNotifier,
    private val fallbackNotifier: FormSubmitAuthEmailNotifier,
) : AuthEmailNotifier {
    override suspend fun notifyAdmin(event: AuthEmailEvent, userEmail: String): Result<Unit> {
        val primary = backendNotifier.notifyAdmin(event, userEmail)
        return if (primary.isSuccess) primary else fallbackNotifier.notifyAdmin(event, userEmail)
    }
}
