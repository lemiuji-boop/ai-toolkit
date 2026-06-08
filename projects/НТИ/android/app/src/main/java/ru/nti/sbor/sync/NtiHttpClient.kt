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

import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import ru.nti.sbor.sync.dto.BatchPushRequest
import ru.nti.sbor.sync.dto.BatchPushResponse
import ru.nti.sbor.sync.dto.HealthResponse
import ru.nti.sbor.sync.dto.LoginRequest
import ru.nti.sbor.sync.dto.LoginResponse
import ru.nti.sbor.sync.dto.OperationDto
import ru.nti.sbor.sync.dto.UserProfileDto
import java.util.concurrent.TimeUnit

/** HTTP-клиент синхронизации без Retrofit. */
class NtiHttpClient(
    baseUrl: String,
    client: OkHttpClient? = null,
) {
    private val normalized = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
    private val http = client ?: OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    private val json = Json { ignoreUnknownKeys = true }
    private val jsonMedia = "application/json".toMediaType()

    fun health(): HealthResponse {
        val request = Request.Builder().url("${normalized}api/v1/health").get().build()
        return execute(request, HealthResponse.serializer())
    }

    fun login(body: LoginRequest): LoginResponse {
        val payload = json.encodeToString(body)
        val request = Request.Builder()
            .url("${normalized}api/v1/mobile/auth/login")
            .header("Content-Type", "application/json")
            .post(payload.toRequestBody(jsonMedia))
            .build()
        return execute(request, LoginResponse.serializer())
    }

    fun currentUser(authorization: String): UserProfileDto {
        val request = Request.Builder()
            .url("${normalized}api/v1/mobile/auth/me")
            .header("Authorization", authorization)
            .get()
            .build()
        return execute(request, UserProfileDto.serializer())
    }

    fun logout(authorization: String) {
        val request = Request.Builder()
            .url("${normalized}api/v1/mobile/auth/logout")
            .header("Authorization", authorization)
            .post("".toRequestBody(jsonMedia))
            .build()
        http.newCall(request).execute().close()
    }

    fun operations(authorization: String): List<OperationDto> {
        val request = Request.Builder()
            .url("${normalized}api/v1/mobile/operations")
            .header("Authorization", authorization)
            .get()
            .build()
        return executeList(request)
    }

    fun pushBatch(authorization: String, body: BatchPushRequest): BatchPushResponse {
        val payload = json.encodeToString(body)
        val request = Request.Builder()
            .url("${normalized}api/v1/mobile/labor-records/batch")
            .header("Authorization", authorization)
            .header("Content-Type", "application/json")
            .post(payload.toRequestBody(jsonMedia))
            .build()
        return execute(request, BatchPushResponse.serializer())
    }

    private inline fun <reified T> execute(request: Request, serializer: kotlinx.serialization.KSerializer<T>): T {
        http.newCall(request).execute().use { response ->
            val body = response.body?.string() ?: ""
            if (!response.isSuccessful) {
                throw IllegalStateException("HTTP ${response.code}: $body")
            }
            return json.decodeFromString(serializer, body)
        }
    }

    private fun executeList(request: Request): List<OperationDto> {
        http.newCall(request).execute().use { response ->
            val body = response.body?.string() ?: ""
            if (!response.isSuccessful) {
                throw IllegalStateException("HTTP ${response.code}: $body")
            }
            return json.decodeFromString(body)
        }
    }
}
