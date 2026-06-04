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

package com.neuropoligon.data.content

import com.neuropoligon.domain.content.Block
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ContentQualityTest {
    @Test fun allTracksHaveUniqueIdsAndUsefulModules() = runTest {
        val tracks = loadAllTracks()
        assertTrue(tracks.size >= 6, "Expected base route and specializations")
        assertEquals(tracks.size, tracks.map { it.id }.distinct().size)
        tracks.forEach { track ->
            assertTrue(track.title.isNotBlank())
            assertTrue(track.description.isNotBlank())
            assertTrue(track.modules.isNotEmpty(), "${track.id} has no modules")
            assertEquals(track.modules.size, track.modules.map { it.id }.distinct().size)
        }
    }

    @Test fun modernTrackCoversCurrentAiSafetyAndPractice() = runTest {
        val track = loadAllTracks().first { it.id == "current_ai" }
        assertTrue(track.modules.size >= 8)
        assertTrue(track.modules.any { it.id == "mcp_context" })
        assertTrue(track.modules.any { it.id == "evals_quality" })
        assertTrue(track.modules.any { module -> module.blocks.any { it is Block.Practice } })
        assertTrue(track.modules.any { module -> module.blocks.any { it is Block.Quiz } })
    }

    @Test fun primaryRouteIsShortEnoughForHumanLearning() = runTest {
        val primary = loadAllTracks().first { it.id == "ai_intro_for_everyone_v1" }
        assertTrue(primary.modules.size in 40..120, "Route should be substantial without template overload")
        assertTrue(primary.description.contains("коротких занятий"))
    }
}
