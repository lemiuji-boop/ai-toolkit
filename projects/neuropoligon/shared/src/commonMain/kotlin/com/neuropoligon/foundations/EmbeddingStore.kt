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

package com.neuropoligon.foundations

import kotlin.math.sqrt

public data class Vector(val x: Double, val y: Double, val z: Double = 0.0)

public data class Neighbor(val word: String, val distance: Double, val vector: Vector)

/**
 * Предрасчитанные эмбеддинги для офлайн-визуализации.
 */
public class EmbeddingStore {
    private val vectors: Map<String, Vector> = DEFAULT_VECTORS

    public fun embed(word: String): Vector? {
        val key = word.lowercase().trim()
        return vectors[key] ?: vectors.entries.firstOrNull { key.contains(it.key) }?.value
    }

    public fun nearest(word: String, n: Int = 5): List<Neighbor> {
        val source = embed(word) ?: return emptyList()
        return vectors
            .filterKeys { it != word.lowercase().trim() }
            .map { (w, v) -> Neighbor(w, euclidean(source, v), v) }
            .sortedBy { it.distance }
            .take(n)
    }

    public fun allPoints(): List<Pair<String, Vector>> = vectors.entries.map { it.key to it.value }

    private fun euclidean(a: Vector, b: Vector): Double {
        val dx = a.x - b.x
        val dy = a.y - b.y
        val dz = a.z - b.z
        return sqrt(dx * dx + dy * dy + dz * dz)
    }

    public companion object {
        private val DEFAULT_VECTORS: Map<String, Vector> = mapOf(
            "кот" to Vector(0.2, 0.8),
            "кошка" to Vector(0.25, 0.78),
            "собака" to Vector(0.3, 0.5),
            "щенок" to Vector(0.32, 0.48),
            "машина" to Vector(0.9, 0.2),
            "автомобиль" to Vector(0.88, 0.22),
            "дом" to Vector(0.5, 0.3),
            "квартира" to Vector(0.52, 0.35),
            "яблоко" to Vector(0.1, 0.1),
            "фрукт" to Vector(0.15, 0.15),
            "банан" to Vector(0.12, 0.18),
            "король" to Vector(0.7, 0.9),
            "королева" to Vector(0.72, 0.88),
            "принц" to Vector(0.68, 0.85),
            "токен" to Vector(0.4, 0.6),
            "слово" to Vector(0.38, 0.58),
            "текст" to Vector(0.42, 0.55),
            "модель" to Vector(0.6, 0.7),
            "нейросеть" to Vector(0.62, 0.72),
            "обучение" to Vector(0.55, 0.65),
            "данные" to Vector(0.5, 0.5),
            "вектор" to Vector(0.45, 0.62),
            "эмбеддинг" to Vector(0.43, 0.64),
            "промпт" to Vector(0.58, 0.75),
            "ответ" to Vector(0.56, 0.73),
            "агент" to Vector(0.65, 0.8),
            "инструмент" to Vector(0.63, 0.78),
            "температура" to Vector(0.48, 0.68),
            "контекст" to Vector(0.46, 0.66),
            "запрос" to Vector(0.54, 0.7),
            "поиск" to Vector(0.52, 0.6),
            "документ" to Vector(0.5, 0.58),
            "код" to Vector(0.8, 0.4),
            "программа" to Vector(0.78, 0.42),
            "функция" to Vector(0.76, 0.44),
            "ошибка" to Vector(0.2, 0.3),
            "успех" to Vector(0.8, 0.9),
            "приватность" to Vector(0.35, 0.85),
            "облако" to Vector(0.85, 0.15),
            "локально" to Vector(0.15, 0.85),
            "квантование" to Vector(0.6, 0.45),
            "дообучение" to Vector(0.58, 0.5),
            "rag" to Vector(0.5, 0.72),
            "llm" to Vector(0.55, 0.74),
            "gpt" to Vector(0.57, 0.76),
            "claude" to Vector(0.59, 0.77),
            "ollama" to Vector(0.2, 0.9),
            "huggingface" to Vector(0.7, 0.55),
            "cursor" to Vector(0.75, 0.6),
            "python" to Vector(0.82, 0.35),
            "kotlin" to Vector(0.84, 0.38),
            "javascript" to Vector(0.83, 0.36),
            "api" to Vector(0.7, 0.5),
            "ключ" to Vector(0.68, 0.48),
            "баланс" to Vector(0.3, 0.4),
            "лимит" to Vector(0.28, 0.38),
            "сеть" to Vector(0.9, 0.5),
            "офлайн" to Vector(0.1, 0.95),
            "онлайн" to Vector(0.95, 0.1),
        )
    }
}
