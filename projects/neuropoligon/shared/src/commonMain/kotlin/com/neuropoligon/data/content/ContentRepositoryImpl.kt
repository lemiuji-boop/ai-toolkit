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

import com.neuropoligon.domain.content.GlossaryEntry
import com.neuropoligon.domain.content.GlossaryFile
import com.neuropoligon.domain.content.GlossaryRepository
import com.neuropoligon.domain.content.ContentRepository
import com.neuropoligon.domain.content.ResourceEntry
import com.neuropoligon.domain.content.ResourcesFile
import com.neuropoligon.domain.content.ResourcesRepository
import com.neuropoligon.domain.content.Track
import com.neuropoligon.domain.content.TracksFile
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.onSubscription
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.json.Json

public class ContentRepositoryImpl : ContentRepository {
    private val json = Json { ignoreUnknownKeys = true; isLenient = true }
    private val mutex = Mutex()
    private val cache = MutableStateFlow<List<Track>>(emptyList())
    private var loaded = false

    override fun observeTracks(): Flow<List<Track>> =
        cache.onSubscription { ensureLoaded() }

    override suspend fun getTracks(): List<Track> {
        ensureLoaded()
        return cache.value
    }

    private suspend fun ensureLoaded() {
        if (loaded) return
        mutex.withLock {
            if (loaded) return
            cache.value = loadAllTracks()
            loaded = true
        }
    }

    private fun normalizeTracksJson(raw: String): String =
        if (raw.trimStart().startsWith("[")) """{"tracks":$raw}""" else raw
}

public class GlossaryRepositoryImpl : GlossaryRepository {
    private val json = Json { ignoreUnknownKeys = true }
    private var cache: List<GlossaryEntry>? = null

    override suspend fun getEntries(): List<GlossaryEntry> {
        cache?.let { return it }
        val entries = json.decodeFromString<GlossaryFile>(loadGlossaryJson()).entries
        cache = entries
        return entries
    }

    override suspend fun findById(id: String): GlossaryEntry? =
        getEntries().firstOrNull { it.id == id || it.term.equals(id, ignoreCase = true) }
}

public class ResourcesRepositoryImpl : ResourcesRepository {
    private val json = Json { ignoreUnknownKeys = true }
    private var cache: List<ResourceEntry>? = null

    override suspend fun getResources(): List<ResourceEntry> {
        cache?.let { return it }
        val resources = json.decodeFromString<ResourcesFile>(loadResourcesJson()).resources
        cache = resources
        return resources
    }
}
