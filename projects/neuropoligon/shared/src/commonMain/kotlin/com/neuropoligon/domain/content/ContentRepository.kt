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

package com.neuropoligon.domain.content

import kotlinx.coroutines.flow.Flow

public interface ContentRepository {
    public fun observeTracks(): Flow<List<Track>>
    public suspend fun getTracks(): List<Track>
}

public interface GlossaryRepository {
    public suspend fun getEntries(): List<GlossaryEntry>
    public suspend fun findById(id: String): GlossaryEntry?
}

public interface ResourcesRepository {
    public suspend fun getResources(): List<ResourceEntry>
}
