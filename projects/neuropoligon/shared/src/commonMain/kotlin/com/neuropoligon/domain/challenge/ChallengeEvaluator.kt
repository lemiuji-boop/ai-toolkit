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

package com.neuropoligon.domain.challenge

import com.neuropoligon.domain.content.Challenge
import com.neuropoligon.domain.content.ChallengeCriterion

public data class ChallengeEvaluation(
    val passed: Boolean,
    val feedback: String,
)

public class ChallengeEvaluator {
    public fun evaluate(
        challenge: Challenge,
        sandboxParams: Map<String, Double> = emptyMap(),
        responseText: String = "",
    ): ChallengeEvaluation = when (val criterion = challenge.criterion) {
        is ChallengeCriterion.SandboxParam -> evaluateParam(criterion, sandboxParams)
        is ChallengeCriterion.ResponseContains -> evaluateContains(criterion, responseText)
    }

    private fun evaluateParam(
        criterion: ChallengeCriterion.SandboxParam,
        params: Map<String, Double>,
    ): ChallengeEvaluation {
        val value = params[criterion.paramName]
            ?: return ChallengeEvaluation(false, "Параметр ${criterion.paramName} не задан.")
        val passed = when (criterion.operator) {
            "<=" -> value <= criterion.value
            ">=" -> value >= criterion.value
            "==" -> value == criterion.value
            else -> false
        }
        return ChallengeEvaluation(
            passed = passed,
            feedback = if (passed) "Отлично! Параметр в нужном диапазоне." else "Попробуйте изменить ${criterion.paramName}.",
        )
    }

    private fun evaluateContains(
        criterion: ChallengeCriterion.ResponseContains,
        responseText: String,
    ): ChallengeEvaluation {
        val passed = responseText.contains(criterion.substring, ignoreCase = true)
        return ChallengeEvaluation(
            passed = passed,
            feedback = if (passed) "Ответ содержит нужную информацию." else "В ответе не найдено: ${criterion.substring}",
        )
    }
}
