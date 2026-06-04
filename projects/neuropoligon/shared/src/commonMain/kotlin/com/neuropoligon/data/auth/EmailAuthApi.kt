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

package com.neuropoligon.data.auth

import com.neuropoligon.domain.auth.AUTH_CLIENT_ANDROID
import com.neuropoligon.domain.auth.AUTH_CLIENT_HEADER
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.HttpResponse
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.http.isSuccess
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

@Serializable
internal data class RegisterRequest(val email: String, val password: String)

@Serializable
internal data class LoginRequest(val email: String, val password: String)

@Serializable
internal data class VerifyRequest(val email: String, val code: String)

@Serializable
internal data class ResendRequest(val email: String)

@Serializable
internal data class AuthMessageResponse(val message: String)

@Serializable
internal data class AuthTokenResponse(
    val token: String,
    val email: String,
    val role: String = "user",
)

internal class EmailAuthApi(
    private val httpClient: HttpClient,
    private val baseUrl: String,
) {
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun health() {
        val response = httpClient.get("$baseUrl/health") {
            header(AUTH_CLIENT_HEADER, AUTH_CLIENT_ANDROID)
        }
        if (!response.status.isSuccess()) {
            throw IllegalStateException(parseErrorMessage(response))
        }
    }

    suspend fun register(email: String, password: String): AuthMessageResponse =
        postJson("$baseUrl/auth/register", RegisterRequest(email, password))

    suspend fun verify(email: String, code: String): AuthTokenResponse =
        postJson("$baseUrl/auth/verify", VerifyRequest(email, code))

    suspend fun resend(email: String): AuthMessageResponse =
        postJson("$baseUrl/auth/resend", ResendRequest(email))

    suspend fun login(email: String, password: String): AuthTokenResponse =
        postJson("$baseUrl/auth/login", LoginRequest(email, password))

    private suspend inline fun <reified T> postJson(url: String, body: Any): T {
        val response = httpClient.post(url) {
            contentType(ContentType.Application.Json)
            header(AUTH_CLIENT_HEADER, AUTH_CLIENT_ANDROID)
            setBody(body)
        }
        if (!response.status.isSuccess()) {
            throw IllegalStateException(parseErrorMessage(response))
        }
        return response.body()
    }

    private suspend fun parseErrorMessage(response: HttpResponse): String {
        val raw = runCatching { response.bodyAsText() }.getOrDefault("")
        val fromJson = runCatching { parseDetailJson(raw) }.getOrNull()
        if (!fromJson.isNullOrBlank()) return fromJson
        return when (response.status.value) {
            401 -> "Неверная почта или пароль."
            403 -> "Доступ запрещён. Проверьте подтверждение почты."
            404 -> "Сервер: путь не найден. Проверьте URL backend."
            in 500..599 -> "Сервер авторизации недоступен (${response.status.value})."
            else -> "Ошибка ${response.status.value}: ${response.status.description}"
        }
    }

    private fun parseDetailJson(raw: String): String? {
        if (raw.isBlank()) return null
        val element = json.parseToJsonElement(raw)
        val detail = element.jsonObject["detail"] ?: return null
        return when (detail) {
            is JsonPrimitive -> detail.content
            is JsonArray -> detail.jsonArray.firstOrNull()?.jsonObject?.get("msg")?.jsonPrimitive?.content
            else -> null
        }
    }
}
