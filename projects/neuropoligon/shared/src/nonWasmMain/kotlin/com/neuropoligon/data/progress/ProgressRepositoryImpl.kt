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

public class ProgressRepositoryImpl(
    private val database: NeuropoligonDatabase,
) : ProgressRepository {
    private val queries = database.progressQueries
    private val completedFlow = MutableStateFlow<List<CompletedBlock>>(emptyList())
    private val cardsFlow = MutableStateFlow<List<RepetitionCard>>(emptyList())
    private val notesFlow = MutableStateFlow<List<UserNote>>(emptyList())

    init {
        refresh()
    }

    private fun refresh() {
        completedFlow.value = queries.selectAllCompleted().executeAsList().map {
            CompletedBlock(it.block_id, it.track_id, it.module_id, it.completed_at)
        }
        notesFlow.value = queries.selectAllNotes().executeAsList().map { UserNote(it.note_id, it.concept_id, it.text, it.updated_at) }
        cardsFlow.value = queries.selectAllCards().executeAsList().map {
            RepetitionCard(it.concept_id, it.interval_days.toInt(), it.ease_factor, it.repetitions.toInt(), it.next_review_at)
        }
    }

    override fun observeCompleted(): Flow<List<CompletedBlock>> = completedFlow.asStateFlow()

    override suspend fun markBlockCompleted(blockId: String, trackId: String, moduleId: String) {
        queries.insertCompleted(blockId, trackId, moduleId, com.neuropoligon.currentTimeMillis())
        refresh()
    }

    override suspend fun saveChallengeResult(challengeId: String, passed: Boolean, feedback: String) {
        queries.insertChallenge(challengeId, if (passed) 1L else 0L, feedback, com.neuropoligon.currentTimeMillis())
    }

    override suspend fun getChallengeResult(challengeId: String): ChallengeResultRecord? {
        val row = queries.selectChallenge(challengeId).executeAsOneOrNull() ?: return null
        return ChallengeResultRecord(challengeId, row.passed == 1L, row.feedback, row.completed_at)
    }

    override fun observeNotes(): Flow<List<UserNote>> = notesFlow.asStateFlow()

    override suspend fun saveNote(noteId: String, conceptId: String, text: String) { queries.upsertNote(noteId, conceptId, text, com.neuropoligon.currentTimeMillis()); refresh() }
    override suspend fun deleteNote(noteId: String) { queries.deleteNote(noteId); refresh() }

    override fun observeCards(): Flow<List<RepetitionCard>> = cardsFlow.asStateFlow()

    override suspend fun upsertCard(card: RepetitionCard) {
        queries.insertCard(
            card.conceptId,
            card.intervalDays.toLong(),
            card.easeFactor,
            card.repetitions.toLong(),
            card.nextReviewAt,
        )
        refresh()
    }

    override suspend fun getDueCards(now: Long): List<RepetitionCard> =
        queries.selectDueCards(now).executeAsList().map {
            RepetitionCard(it.concept_id, it.interval_days.toInt(), it.ease_factor, it.repetitions.toInt(), it.next_review_at)
        }

    override suspend fun mergeFromGuest(other: ProgressRepository) {
        other.observeCompleted().collect { blocks ->
            blocks.forEach { markBlockCompleted(it.blockId, it.trackId, it.moduleId) }
        }
    }
}
