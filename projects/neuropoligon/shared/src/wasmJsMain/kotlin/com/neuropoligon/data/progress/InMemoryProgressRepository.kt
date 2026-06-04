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

package com.neuropoligon.data.progress

import com.neuropoligon.domain.progress.ChallengeResultRecord
import com.neuropoligon.domain.progress.CompletedBlock
import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.domain.progress.RepetitionCard
import com.neuropoligon.domain.progress.UserNote
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Web/Wasm: SQLDelight JDBC недоступен — храним прогресс в памяти сессии.
 */
public class InMemoryProgressRepository : ProgressRepository {
    private val completed = MutableStateFlow<List<CompletedBlock>>(emptyList())
    private val cards = MutableStateFlow<List<RepetitionCard>>(emptyList())
    private val notes = MutableStateFlow<List<UserNote>>(emptyList())
    private val challenges = mutableMapOf<String, ChallengeResultRecord>()

    override fun observeCompleted(): Flow<List<CompletedBlock>> = completed.asStateFlow()

    override suspend fun markBlockCompleted(blockId: String, trackId: String, moduleId: String) {
        val list = completed.value.filterNot { it.blockId == blockId } +
            CompletedBlock(blockId, trackId, moduleId, com.neuropoligon.currentTimeMillis())
        completed.value = list
    }

    override suspend fun saveChallengeResult(challengeId: String, passed: Boolean, feedback: String) {
        challenges[challengeId] = ChallengeResultRecord(
            challengeId, passed, feedback, com.neuropoligon.currentTimeMillis(),
        )
    }

    override suspend fun getChallengeResult(challengeId: String): ChallengeResultRecord? =
        challenges[challengeId]

    override fun observeNotes(): Flow<List<UserNote>> = notes.asStateFlow()

    override suspend fun saveNote(noteId: String, conceptId: String, text: String) { notes.value = notes.value.filterNot { it.noteId == noteId } + UserNote(noteId, conceptId, text, com.neuropoligon.currentTimeMillis()) }
    override suspend fun deleteNote(noteId: String) { notes.value = notes.value.filterNot { it.noteId == noteId } }

    override fun observeCards(): Flow<List<RepetitionCard>> = cards.asStateFlow()

    override suspend fun upsertCard(card: RepetitionCard) {
        cards.value = cards.value.filterNot { it.conceptId == card.conceptId } + card
    }

    override suspend fun getDueCards(now: Long): List<RepetitionCard> =
        cards.value.filter { it.nextReviewAt <= now }

    override suspend fun mergeFromGuest(other: ProgressRepository) {
        other.observeCompleted().collect { blocks ->
            blocks.forEach { markBlockCompleted(it.blockId, it.trackId, it.moduleId) }
        }
    }
}
