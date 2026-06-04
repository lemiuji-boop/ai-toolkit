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

import com.neuropoligon.domain.progress.RepetitionCard

/**
 * SM-2-подобный планировщик интервального повторения.
 */
public class SpacedRepetitionScheduler {
    public fun scheduleNext(
        current: RepetitionCard?,
        quality: Int,
        now: Long,
    ): RepetitionCard {
        val conceptId = current?.conceptId ?: "unknown"
        if (current == null) {
            return RepetitionCard(
                conceptId = conceptId,
                intervalDays = 1,
                easeFactor = 2.5,
                repetitions = 1,
                nextReviewAt = now + DAY_MS,
            )
        }
        var ease = current.easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease = ease.coerceAtLeast(1.3)
        val repetitions = if (quality < 3) 0 else current.repetitions + 1
        val intervalDays = when {
            quality < 3 -> 1
            repetitions == 1 -> 1
            repetitions == 2 -> 6
            else -> (current.intervalDays * ease).toInt().coerceAtLeast(1)
        }
        return RepetitionCard(
            conceptId = conceptId,
            intervalDays = intervalDays,
            easeFactor = ease,
            repetitions = repetitions,
            nextReviewAt = now + intervalDays * DAY_MS,
        )
    }

    public companion object {
        private const val DAY_MS: Long = 86_400_000L
    }
}
