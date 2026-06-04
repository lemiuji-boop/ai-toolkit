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

/**
 * Токен после токенизации.
 */
public data class Token(
    val text: String,
    val id: Int,
)

/**
 * Упрощённый BPE-токенизатор: посимвольный старт + слияния по частым парам.
 */
public class SimpleBpeTokenizer(
  private val merges: List<Pair<String, String>> = DEFAULT_MERGES,
) {
    private val mergeRanks: Map<Pair<String, String>, Int> =
        merges.withIndex().associate { (index, pair) -> pair to index }

    public fun tokenize(text: String): List<Token> {
        if (text.isEmpty()) return emptyList()
        var pieces = text.map { it.toString() }
        var changed = true
        while (changed) {
            changed = false
            var bestIndex = -1
            var bestRank = Int.MAX_VALUE
            for (index in 0 until pieces.size - 1) {
                val pair = pieces[index] to pieces[index + 1]
                val rank = mergeRanks[pair] ?: continue
                if (rank < bestRank) {
                    bestRank = rank
                    bestIndex = index
                }
            }
            if (bestIndex >= 0) {
                val merged = pieces[bestIndex] + pieces[bestIndex + 1]
                pieces = pieces.take(bestIndex) + merged + pieces.drop(bestIndex + 2)
                changed = true
            }
        }
        return pieces.mapIndexed { index, piece -> Token(text = piece, id = index) }
    }

    public companion object {
        private val DEFAULT_MERGES: List<Pair<String, String>> = listOf(
            " " to "т",
            "т" to "о",
            "о" to "к",
            " " to "е",
            "е" to "н",
            " " to "и",
            "и" to "и",
            " " to "м",
            "м" to "о",
            "о" to "д",
            "д" to "е",
            " " to "л",
            "л" to "ь",
        )
    }
}
