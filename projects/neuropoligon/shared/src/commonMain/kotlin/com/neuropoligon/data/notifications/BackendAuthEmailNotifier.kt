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
import com.neuropoligon.domain.notifications.AUTH_NOTIFY_WEBHOOK_TOKEN_KEY
import com.neuropoligon.domain.notifications.AUTH_NOTIFY_WEBHOOK_URL_KEY
import com.neuropoligon.platform.SecureStorage
import io.ktor.client.HttpClient
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.http.isSuccess
import kotlinx.serialization.Serializable

/**
 * Отправка уведомлений в пользовательский backend webhook (дальше SMTP на стороне сервера).
 */
public class BackendAuthEmailNotifier(
    private val httpClient: HttpClient,
    private val secureStorage: SecureStorage,
) : AuthEmailNotifier {
    override suspend fun notifyAdmin(event: AuthEmailEvent, userEmail: String): Result<Unit> {
        val webhookUrl = secureStorage.get(AUTH_NOTIFY_WEBHOOK_URL_KEY)?.trim().orEmpty()
        if (webhookUrl.isEmpty()) {
            return Result.failure(IllegalStateException("Webhook URL не задан."))
        }
        val token = secureStorage.get(AUTH_NOTIFY_WEBHOOK_TOKEN_KEY)?.trim().orEmpty()
        val payload = WebhookPayload(
            event = event.name,
            userEmail = userEmail,
            app = "Нейрополигон",
        )
        return runCatching {
            val response = httpClient.post(webhookUrl) {
                contentType(ContentType.Application.Json)
                if (token.isNotEmpty()) {
                    header("Authorization", "Bearer $token")
                }
                setBody(payload)
            }
            if (!response.status.isSuccess()) {
                error("Webhook вернул код ${response.status.value}")
            }
        }
    }
}

@Serializable
private data class WebhookPayload(
    val event: String,
    val userEmail: String,
    val app: String,
)
