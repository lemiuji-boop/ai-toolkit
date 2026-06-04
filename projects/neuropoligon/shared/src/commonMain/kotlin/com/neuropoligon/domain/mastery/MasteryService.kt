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

package com.neuropoligon.domain.mastery

import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.domain.progress.RepetitionCard

public class MasteryService(
    private val progressRepository: ProgressRepository,
    private val scheduler: SpacedRepetitionScheduler,
) {
    public suspend fun recordConceptReview(conceptId: String, quality: Int, now: Long = com.neuropoligon.currentTimeMillis()) {
        val all = progressRepository.getDueCards(now + Long.MAX_VALUE / 2)
        val current = all.firstOrNull { it.conceptId == conceptId }
        val next = scheduler.scheduleNext(current, quality, now).copy(conceptId = conceptId)
        progressRepository.upsertCard(next)
    }

    public suspend fun getDueConcepts(now: Long = com.neuropoligon.currentTimeMillis()): List<RepetitionCard> =
        progressRepository.getDueCards(now)
}
