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

package ru.nti.sbor.sync.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class LaborRecordDto(
    @SerialName("client_id") val clientId: String,
    val date: String,
    val worker: String,
    val product: String,
    val operation: String,
    val value: Double,
    val unit: String,
    val note: String = "",
)

@Serializable
data class BatchPushRequest(
    val records: List<LaborRecordDto>,
)

@Serializable
data class BatchPushResponse(
    val accepted: List<AcceptedRecord>,
    val errors: List<BatchError> = emptyList(),
)

@Serializable
data class AcceptedRecord(
    @SerialName("client_id") val clientId: String,
    @SerialName("server_id") val serverId: String,
)

@Serializable
data class BatchError(
    @SerialName("client_id") val clientId: String,
    val message: String,
)

@Serializable
data class OperationDto(
    val id: Long? = null,
    val name: String,
    val active: Boolean = true,
)

@Serializable
data class HealthResponse(
    val status: String,
)
