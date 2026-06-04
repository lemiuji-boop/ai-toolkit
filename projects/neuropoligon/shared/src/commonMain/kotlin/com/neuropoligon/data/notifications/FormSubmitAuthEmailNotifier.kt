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

import com.neuropoligon.domain.notifications.ADMIN_NOTIFY_EMAIL
import com.neuropoligon.domain.notifications.AuthEmailEvent
import com.neuropoligon.domain.notifications.AuthEmailNotifier
import io.ktor.client.HttpClient
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.http.isSuccess
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
/**
 * Отправка уведомлений на почту администратора через FormSubmit (без отдельного бэкенда).
 */
public class FormSubmitAuthEmailNotifier(
    private val httpClient: HttpClient,
) : AuthEmailNotifier {
    override suspend fun notifyAdmin(event: AuthEmailEvent, userEmail: String): Result<Unit> {
        val eventLabel = when (event) {
            AuthEmailEvent.SignUp -> "регистрация"
            AuthEmailEvent.SignIn -> "вход"
            AuthEmailEvent.SignOut -> "выход"
        }
        val body = FormSubmitPayload(
            email = userEmail,
            message = "Событие: $eventLabel\nПользователь: $userEmail\nПриложение: Нейрополигон",
            subject = "Нейрополигон — $eventLabel",
        )
        return runCatching {
            val response = httpClient.post("https://formsubmit.co/ajax/$ADMIN_NOTIFY_EMAIL") {
                contentType(ContentType.Application.Json)
                setBody(body)
            }
            if (!response.status.isSuccess()) {
                error("Не удалось отправить письмо (код ${response.status.value})")
            }
        }
    }
}

@Serializable
private data class FormSubmitPayload(
    val email: String,
    val message: String,
    @SerialName("_subject") val subject: String,
    @SerialName("_template") val template: String = "table",
    @SerialName("_captcha") val captcha: String = "false",
)
