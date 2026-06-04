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

import com.neuropoligon.resources.Res
import org.jetbrains.compose.resources.ExperimentalResourceApi

@OptIn(ExperimentalResourceApi::class)
internal suspend fun readAssetFile(name: String): String =
    Res.readBytes("files/$name").decodeToString()

@OptIn(ExperimentalResourceApi::class)
internal suspend fun loadIntroTrack(): com.neuropoligon.domain.content.Track {
    val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true; isLenient = true }
    val seed = json.decodeFromString<AiIntroCourseSeedFile>(readAssetFile("ai_intro_course_seed.json"))
    val base = AiIntroCourseSeedConverter.convert(seed)
    return CourseCurriculumExpander.expand(base)
}

internal suspend fun loadTracksJson(): String {
    val seedRaw = readAssetFile("ai_intro_course_seed.json")
    val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true; isLenient = true }
    val seed = json.decodeFromString<AiIntroCourseSeedFile>(seedRaw)
    val introTrack = AiIntroCourseSeedConverter.convert(seed)
    return json.encodeToString(com.neuropoligon.domain.content.TracksFile(listOf(introTrack)))
}

internal suspend fun loadAllTracks(): List<com.neuropoligon.domain.content.Track> {
    val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true; isLenient = true }
    val extras = listOf("track_foundations.json", "track_model_picker.json", "track_local_ai.json", "track_finetuning.json", "track_builder.json", "track_current_ai.json")
        .flatMap { name -> json.decodeFromString<com.neuropoligon.domain.content.TracksFile>(normalize(readAssetFile(name))).tracks }
    return (listOf(loadIntroTrack()) + extras).distinctBy { it.id }
}

internal suspend fun loadGlossaryJson(): String = readAssetFile("glossary.json")

internal suspend fun loadResourcesJson(): String {
    val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true; isLenient = true }
    val base = json.decodeFromString<com.neuropoligon.domain.content.ResourcesFile>(readAssetFile("resources.json"))
    val seed = json.decodeFromString<AiIntroCourseSeedFile>(readAssetFile("ai_intro_course_seed.json"))
    val fromSeed = seed.resources.mapIndexed { index, resource ->
        com.neuropoligon.domain.content.ResourceEntry(
            id = "seed_${index}_${resource.type}",
            name = resource.title,
            category = resourceTypeLabel(resource.type),
            whatItIs = "Материал курса «${seed.title}»",
            useFor = "Уровень ${resource.level}+",
            officialUrl = resource.url,
        )
    }
    val merged = (base.resources + fromSeed).distinctBy { it.officialUrl }
    return json.encodeToString(com.neuropoligon.domain.content.ResourcesFile(merged))
}

private fun resourceTypeLabel(type: String): String = when (type) {
    "course" -> "Курсы"
    "practice" -> "Практика"
    "guide" -> "Гайды"
    "safety" -> "Безопасность"
    "android" -> "Android"
    else -> "Ресурсы"
}

private fun mergeTracksJson(primary: String, others: List<String>): String {
    val json = kotlinx.serialization.json.Json { ignoreUnknownKeys = true }
    val tracks = mutableListOf<com.neuropoligon.domain.content.Track>()
    tracks.addAll(json.decodeFromString<com.neuropoligon.domain.content.TracksFile>(normalize(primary)).tracks)
    others.forEach { part ->
        tracks.addAll(json.decodeFromString<com.neuropoligon.domain.content.TracksFile>(normalize(part)).tracks)
    }
    return json.encodeToString(com.neuropoligon.domain.content.TracksFile(tracks))
}

private fun normalize(raw: String): String =
    if (raw.trimStart().startsWith("[")) """{"tracks":$raw}""" else raw
