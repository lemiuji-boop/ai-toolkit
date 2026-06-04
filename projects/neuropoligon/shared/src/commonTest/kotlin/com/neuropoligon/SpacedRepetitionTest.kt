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

package com.neuropoligon

import com.neuropoligon.domain.mastery.SpacedRepetitionScheduler
import com.neuropoligon.domain.progress.RepetitionCard
import kotlin.test.Test
import kotlin.test.assertTrue

class SpacedRepetitionTest {
  private val scheduler = SpacedRepetitionScheduler()

    @Test
    fun firstReviewSchedulesOneDay() {
        val card = scheduler.scheduleNext(null, quality = 4, now = 0L)
        assertTrue(card.intervalDays >= 1)
    }

    @Test
    fun lowQualityResetsInterval() {
        val existing = RepetitionCard("c1", 10, 2.5, 3, 1000L)
        val card = scheduler.scheduleNext(existing, quality = 2, now = 1000L)
        assertTrue(card.intervalDays <= 1)
    }
}
