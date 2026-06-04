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
import com.neuropoligon.domain.content.DifficultyLevel
import com.neuropoligon.domain.content.LearningMode
import com.neuropoligon.domain.content.Module
import com.neuropoligon.domain.content.QuizQuestion
import com.neuropoligon.domain.content.Track

/**
 * Преобразует seed-курс «Введение в ИИ-технологии» в линейный трек приложения.
 */
internal object AiIntroCourseSeedConverter {
    fun convert(seed: AiIntroCourseSeedFile): Track {
        val lessonModules = seed.modules
            .sortedBy { it.order }
            .flatMap { chapter -> chapter.lessons.sortedBy { it.order }.map { lesson -> chapter to lesson } }
            .mapIndexed { index, (chapter, lesson) ->
                toLessonModule(seed, chapter, lesson, index + 1)
            }

        val intro = introModule(seed)
        return Track(
            id = seed.courseId,
            title = seed.title,
            description = buildCourseDescription(seed),
            modules = listOf(intro) + lessonModules,
            requiresApiKey = false,
            minLevel = DifficultyLevel.Zero,
            learningModes = seed.learningModes.map { LearningMode(it.id, it.title, it.description) },
            targetAudience = seed.targetAudience,
        )
    }

    private fun introModule(seed: AiIntroCourseSeedFile): Module = Module(
        id = "intro-course",
        title = "Старт. Как проходить курс",
        summary = "Ознакомление с маршрутами и инструментами обучения.",
        chapterId = "intro",
        chapterTitle = "Введение",
        chapterOrder = 0,
        lessonOrder = 0,
        durationMinutes = 8,
        minLevel = DifficultyLevel.Zero,
        blocks = listOf(
            Block.Explanation(
                markdownByLevel = mapOf(
                    DifficultyLevel.Zero to """
                        Добро пожаловать в курс **${seed.title}**.

                        Как учиться:
                        1) Читайте теорию и нажимайте на [[термин|термины]] для выносок.
                        2) Выполняйте блок **Практика** — копируйте промт и работайте с ИИ.
                        3) Пройдите **Мини-тест**, если он есть в уроке.
                        4) Нажмите **Следующий урок**.

                        Маршруты:
                        - Быстрый (7 дней) — первые ключевые уроки.
                        - Основной (8 недель) — полный базовый путь.
                        - Глубокий (12 недель) — все уроки, включая продвинутые темы.

                        Для кого курс: ${seed.targetAudience.joinToString(", ")}.
                    """.trimIndent(),
                ),
                coreForAll = true,
            ),
            Block.Practice(
                title = "Первый шаг",
                prompt = "Сформулируй одну личную задачу, где ИИ может помочь уже сегодня. Опиши цель, ограничения и как проверишь результат.",
            ),
        ),
    )

    private fun toLessonModule(
        seed: AiIntroCourseSeedFile,
        chapter: SeedModule,
        lesson: SeedLesson,
        lessonIndex: Int,
    ): Module {
        val blocks = mutableListOf<Block>()
        blocks += Block.Explanation(
            markdownByLevel = mapOf(
                DifficultyLevel.Zero to buildLessonMarkdown(seed, chapter, lesson),
                DifficultyLevel.Advanced to buildLessonMarkdownAdvanced(chapter, lesson),
            ),
            coreForAll = true,
        )
        lesson.practice?.let { practice ->
            blocks += Block.Practice(title = practice.title, prompt = practice.prompt)
            blocks += Block.Sandbox(
                sandboxType = com.neuropoligon.domain.content.SandboxType.SystemPrompt,
                config = com.neuropoligon.domain.content.SandboxConfig(
                    prompt = practice.prompt,
                    defaultTemperature = 0.4,
                ),
            )
        }
        if (lesson.quiz.isNotEmpty()) {
            blocks += Block.Quiz(
                questions = lesson.quiz.map { q ->
                    QuizQuestion(
                        question = q.question,
                        options = q.options,
                        answerIndex = q.answerIndex,
                        explanation = q.explanation,
                    )
                },
            )
        }
        val chapterResources = seed.resources.filter { it.level <= chapter.level + 1 }.take(2)
        if (chapterResources.isNotEmpty()) {
            val links = chapterResources.joinToString("\n") { r ->
                "- [${r.title}](${r.url})"
            }
            blocks += Block.Explanation(
                markdown = "Дополнительные материалы:\n$links",
                coreForAll = true,
            )
        }
        return Module(
            id = lesson.id,
            title = "Урок $lessonIndex. ${lesson.title}",
            summary = chapter.summary,
            chapterId = chapter.id,
            chapterTitle = chapter.title,
            chapterOrder = chapter.order,
            lessonOrder = lesson.order,
            durationMinutes = lesson.durationMinutes,
            minLevel = mapSeedLevel(chapter.level),
            blocks = blocks,
        )
    }

    private fun buildCourseDescription(seed: AiIntroCourseSeedFile): String =
        "Линейный курс из ${seed.modules.sumOf { it.lessons.size }} уроков. " +
            "Маршруты: ${seed.learningModes.joinToString { it.title }}"

    private fun buildLessonMarkdown(
        seed: AiIntroCourseSeedFile,
        chapter: SeedModule,
        lesson: SeedLesson,
    ): String {
        val body = lessonContent(lesson.id, chapter, lesson)
        return """
            **Раздел ${chapter.order}: ${chapter.title}**

            ${chapter.summary}

            ## ${lesson.title}

            $body

            Время урока: ~${lesson.durationMinutes} мин.
        """.trimIndent()
    }

    private fun buildLessonMarkdownAdvanced(chapter: SeedModule, lesson: SeedLesson): String =
        """
            ### ${chapter.title} — ${lesson.title}

            Фокус: применимость в рабочих сценариях, проверка гипотез и фиксация ограничений модели.
            После практики зафиксируйте: входные данные, ожидаемый формат ответа, критерии проверки.
        """.trimIndent()

    private fun mapSeedLevel(level: Int): DifficultyLevel = when {
        level <= 0 -> DifficultyLevel.Zero
        level == 1 -> DifficultyLevel.Beginner
        level == 2 -> DifficultyLevel.Intermediate
        else -> DifficultyLevel.Advanced
    }

    private fun lessonContent(id: String, chapter: SeedModule, lesson: SeedLesson): String = when (id) {
        "m01_l01" -> """
            [[ИИ|Искусственный интеллект]] — это программы, которые учатся на данных и помогают решать задачи: текст, поиск, рекомендации, распознавание.

            Важно: ИИ не «думает» как человек. Он строит ответ по шаблонам из обучения и может ошибаться.

            Примеры в жизни: автодополнение, перевод, голосовые помощники, рекомендации в магазинах.
        """.trimIndent()
        "m01_l02" -> """
            ИИ уже рядом: камера телефона, поиск, банковские уведомления, навигатор, музыкальные рекомендации, фильтрация спама.

            Полезно вести личный список «где я уже использую ИИ» — это снижает страх и показывает практическую пользу.
        """.trimIndent()
        "m01_l03" -> """
            ИИ хорошо: черновики, структурирование, объяснения, идеи, рутинная обработка текста.

            ИИ плохо без проверки: медицина, юридические решения, финансовые советы, факты «из головы».

            Правило: чем выше риск, тем сильнее нужна [[проверка|проверка фактов]] человеком.
        """.trimIndent()
        "m02_l01" -> """
            До нейросетей ИИ строили на правилах «если-то». Это работало в узких задачах, но плохо масштабировалось.

            Современный подход: модель учится на примерах и обобщает закономерности.
        """.trimIndent()
        "m02_l02" -> """
            Этапы: правила → экспертные системы → [[машинное обучение]] → глубокое обучение → трансформеры → генеративный ИИ.

            Сейчас чат-боты — это в основном большие языковые модели (LLM).
        """.trimIndent()
        "m03_l01" -> """
            Качество ИИ зависит от данных: полнота, ошибки, смещения, приватность.

            Перед задачей спросите: какие данные нужны, откуда они, можно ли их передавать в облако.
        """.trimIndent()
        "m03_l02" -> """
            Ошибки возникают из-за неполного контекста, устаревших знаний, двусмысленных формулировок и «галлюцинаций».

            Просите модель отделять факты от предположений и указывать, что нужно проверить.
        """.trimIndent()
        "m04_l01" -> """
            Типы: классическое ML, компьютерное зрение, NLP, генеративный ИИ, [[агент|агентные системы]].

            Для каждой задачи выбирайте тип инструмента, а не «один чат на всё».
        """.trimIndent()
        "m04_l02" -> """
            Агент — цепочка шагов: план → действие → проверка. Критичны подтверждения пользователя на рискованных шагах.
        """.trimIndent()
        "m05_l01" -> """
            [[LLM]] предсказывает следующий фрагмент текста. Контекст ограничен: модель «видит» только переданный диалог и документы.

            Чем точнее контекст, тем полезнее ответ.
        """.trimIndent()
        "m06_l01" -> """
            Хороший [[промт]]: роль + задача + контекст + формат + критерии качества + ограничения.

            Пример структуры есть в блоке практики ниже.
        """.trimIndent()
        "m06_l02" -> """
            Улучшайте ответ итерациями: черновик → критика → улучшенная версия.

            Это дешевле, чем пытаться получить идеал с первого запроса.
        """.trimIndent()
        "m07_l01" -> """
            Для документов: резюме, факты, риски, вопросы, таблица действий. Запрещайте добавлять факты вне источника.
        """.trimIndent()
        "m08_l01" -> """
            Для изображений важны: объект, стиль, композиция, свет, настроение, ограничения (без текста/логотипов).
        """.trimIndent()
        "m09_l01" -> """
            ИИ-наставник работает лучше по шагам: маленькая тема → вопрос → ответ ученика → обратная связь.
        """.trimIndent()
        "m10_l01" -> """
            Агент полезен, когда задача состоит из нескольких действий и нужна проверка промежуточных результатов.
        """.trimIndent()
        "m11_l01" -> """
            Облако — быстро стартовать. Локально — приватность. API — встраивание в продукт. Выбор зависит от рисков и бюджета.
        """.trimIndent()
        "m12_l01" -> """
            [[Галлюцинация]] — уверенный, но неверный ответ. Лечится проверкой источников и ограничением «отвечай только по тексту».
        """.trimIndent()
        "m13_l01" -> """
            Этика и право: не передавайте чувствительные данные, проверяйте авторские ограничения, фиксируйте ответственность человека.
        """.trimIndent()
        "m14_l01" -> """
            Финал: соберите личную карту применения ИИ — 3 сценария (простой, рабочий, обучающий) с промтами, рисками и проверкой.
        """.trimIndent()
        else -> """
            Тема урока: ${lesson.title}.

            ${chapter.summary}

            Используйте практический блок ниже, чтобы закрепить материал на своей задаче.
        """.trimIndent()
    }
}
