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

/**
 * Совет авторов курса: моделирует подготовку материала разными ролями.
 * Идея: педагогическая логика хранится отдельно от UI и может расширяться.
 */
public object CourseAuthoringCouncil {
    public val experts: List<ExpertRole> = listOf(
        ExpertRole("Преподаватель-практик", "Объясняет просто и через примеры."),
        ExpertRole("Профессор ML", "Добавляет теорию и корректные формулировки."),
        ExpertRole("Доцент по NLP", "Следит за точностью терминов и связностью тем."),
        ExpertRole("Ведущий инженер", "Проверяет применимость в реальном коде."),
    )

    public fun buildEditorialNotes(): List<String> = listOf(
        "Вести ученика линейно: от базовых понятий к управлению моделью.",
        "Каждый термин объяснять в отдельной выноске по нажатию.",
        "Ссылки на ресурсы размещать прямо в тексте уроков, а не на отдельном экране.",
        "После теории обязательно давать практический шаг и короткий self-check.",
    )
}

public data class ExpertRole(
    val title: String,
    val mission: String,
)
