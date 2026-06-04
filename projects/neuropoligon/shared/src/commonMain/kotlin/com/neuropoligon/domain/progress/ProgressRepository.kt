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

package com.neuropoligon.domain.progress

import kotlinx.coroutines.flow.Flow

public data class CompletedBlock(
    val blockId: String,
    val trackId: String,
    val moduleId: String,
    val completedAt: Long,
)

public data class ChallengeResultRecord(
    val challengeId: String,
    val passed: Boolean,
    val feedback: String,
    val completedAt: Long,
)

public data class UserNote(
    val noteId: String,
    val conceptId: String,
    val text: String,
    val updatedAt: Long,
)

public data class RepetitionCard(
    val conceptId: String,
    val intervalDays: Int,
    val easeFactor: Double,
    val repetitions: Int,
    val nextReviewAt: Long,
)

public interface ProgressRepository {
    public fun observeCompleted(): Flow<List<CompletedBlock>>
    public suspend fun markBlockCompleted(blockId: String, trackId: String, moduleId: String)
    public suspend fun saveChallengeResult(challengeId: String, passed: Boolean, feedback: String)
    public suspend fun getChallengeResult(challengeId: String): ChallengeResultRecord?
    public fun observeNotes(): Flow<List<UserNote>>
    public suspend fun saveNote(noteId: String, conceptId: String, text: String)
    public suspend fun deleteNote(noteId: String)
    public fun observeCards(): Flow<List<RepetitionCard>>
    public suspend fun upsertCard(card: RepetitionCard)
    public suspend fun getDueCards(now: Long): List<RepetitionCard>
    public suspend fun mergeFromGuest(other: ProgressRepository)
}
