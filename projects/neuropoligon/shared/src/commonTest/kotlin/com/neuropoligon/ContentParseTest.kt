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

import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.domain.content.TracksFile
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ContentParseTest {
    private val json = Json { ignoreUnknownKeys = true }

    @Test
    fun parsesTrackWithOptionalFields() {
        val raw = """
            {"tracks":[{"id":"t1","title":"T","description":"D","minLevel":"zero","modules":[]}]}
        """.trimIndent()
        val tracks = json.decodeFromString<TracksFile>(raw).tracks
        assertEquals(1, tracks.size)
        assertEquals(DifficultyLevel.Zero, tracks[0].minLevel)
    }

    @Test
    fun missingOptionalUsesDefaults() {
        val raw = """{"tracks":[{"id":"t","title":"x","description":"y"}]}"""
        val track = json.decodeFromString<TracksFile>(raw).tracks.first()
        assertTrue(track.modules.isEmpty())
        assertEquals(false, track.requiresApiKey)
    }
}
