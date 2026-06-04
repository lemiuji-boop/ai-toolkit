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
import com.neuropoligon.domain.content.Module
import com.neuropoligon.domain.content.QuizQuestion
import com.neuropoligon.domain.content.SandboxConfig
import com.neuropoligon.domain.content.SandboxType
import com.neuropoligon.domain.content.Track

/**
 * Превращает базовые темы в четыре содержательных шага: понять, попробовать, проверить и применить.
 */
internal object CourseCurriculumExpander {
    private const val MICRO_LESSONS_PER_BASE: Int = 4

    fun expand(track: Track): Track {
        val intro = track.modules.firstOrNull { it.id == "intro-course" }
        val baseLessons = track.modules.filter { it.id != "intro-course" }
        val expanded = baseLessons.flatMap { module -> expandModule(module) }
        return track.copy(
            modules = listOfNotNull(intro) + expanded,
            description = track.description +
                " Практическая программа: ${expanded.size} коротких занятий.",
        )
    }

    private fun expandModule(base: Module): List<Module> {
        val baseBlocks = base.blocks
        val basePractice = baseBlocks.filterIsInstance<Block.Practice>().firstOrNull()
        val baseQuiz = baseBlocks.filterIsInstance<Block.Quiz>().firstOrNull()
        return (1..MICRO_LESSONS_PER_BASE).map { part ->
            val partId = "${base.id}_p${part.toString().padStart(2, '0')}"
            val blocks = mutableListOf<Block>()
            blocks += Block.Explanation(
                markdownByLevel = mapOf(
                    DifficultyLevel.Zero to buildMicroMarkdown(base, part),
                    DifficultyLevel.Advanced to buildMicroMarkdownAdvanced(base, part),
                ),
                coreForAll = true,
            )
            blocks += Block.Practice(
                title = basePractice?.title ?: "Практика",
                prompt = buildMicroPractice(base, basePractice?.prompt.orEmpty(), part),
            )
            if (part % 5 == 0) {
                blocks += Block.Quiz(questions = microQuiz(base, part, baseQuiz))
            }
            if (part % 3 == 0) {
                blocks += Block.Sandbox(
                    sandboxType = SandboxType.SystemPrompt,
                    config = SandboxConfig(
                        prompt = basePractice?.prompt.orEmpty(),
                        defaultTemperature = 0.3 + (part % 5) * 0.1,
                    ),
                )
            }
            base.copy(
                id = partId,
                title = "${base.title} · часть $part/$MICRO_LESSONS_PER_BASE",
                durationMinutes = maxOf(3, (base.durationMinutes ?: 12) / 6),
                blocks = blocks,
            )
        }
    }

    private fun buildMicroMarkdown(base: Module, part: Int): String {
        val template = MICRO_THEORY_TEMPLATES[(part - 1) % MICRO_THEORY_TEMPLATES.size]
        val focus = MICRO_FOCUS_TOPICS[(part - 1) % MICRO_FOCUS_TOPICS.size]
        val example = MICRO_EXAMPLES[(part - 1) % MICRO_EXAMPLES.size]
        val mistake = MICRO_MISTAKES[(part - 1) % MICRO_MISTAKES.size]
        val deep = MICRO_DEEP_DIVES[(part - 1) % MICRO_DEEP_DIVES.size]
        val promptTemplate = buildPromptTemplate(base, part)
        return """
            ## ${base.title}

            **Часть $part из $MICRO_LESSONS_PER_BASE** · фокус: $focus

            ${base.summary?.let { "### Контекст раздела\n$it\n" } ?: ""}

            ### О чём этот фрагмент
            $template

            ### Разбор на примере
            $example

            :::important
            $mistake
            :::

            ### Подробнее
            $deep

            :::template
            $promptTemplate
            :::

            ### Чек-лист после урока
            - Сформулируйте **одну** реальную задачу, где примените идею.
            - Запишите ожидаемый формат ответа (список, таблица, письмо).
            - Отметьте, **что проверите человеком** до принятия решения.

            :::prompt
            ${buildMicroPractice(base, "", part)}
            :::
        """.trimIndent()
    }

    private fun buildPromptTemplate(base: Module, part: Int): String =
        """
        Роль: наставник по ИИ.
        Тема: ${base.title} (часть $part).
        Задача: объясни материал и дай 3 практических шага.
        Формат: нумерованный список, до 200 слов.
        Ограничение: не выдумывай факты; помечай предположения.
        """.trimIndent()

    private fun buildMicroMarkdownAdvanced(base: Module, part: Int): String =
        """
            ### Углубление · часть $part

            Сформулируйте гипотезу, проверьте ответ модели на 2 независимых источниках, зафиксируйте ограничения.
            Тема: ${base.chapterTitle ?: base.title}.
        """.trimIndent()

    private fun buildMicroPractice(base: Module, seedPrompt: String, part: Int): String {
        val step = PRACTICE_STEPS[(part - 1) % PRACTICE_STEPS.size]
        val seed = seedPrompt.ifBlank { "Помоги мне разобраться с темой «${base.title}»." }
        return """
            $seed

            Дополнительно (часть $part): $step
        """.trimIndent()
    }

    private fun microQuiz(base: Module, part: Int, seed: Block.Quiz?): List<QuizQuestion> {
        seed?.questions?.take(2)?.let { return it }
        val idx = (part - 1) % MICRO_QUIZ.size
        val item = MICRO_QUIZ[idx]
        return listOf(
            QuizQuestion(
                question = "${item.question} (${base.chapterTitle ?: "урок"})",
                options = item.options,
                answerIndex = item.answerIndex,
                explanation = item.explanation,
            ),
        )
    }

    private val MICRO_THEORY_TEMPLATES: List<String> = listOf(
        "[[ИИ]] помогает ускорять рутину, но ответ нужно проверять, если решение влияет на деньги, здоровье или репутацию.",
        "Хороший [[промт]] отвечает на вопросы: кто вы, что нужно, в каком формате, какие ограничения и как проверить результат.",
        "[[LLM]] не «знает всё» — она предсказывает следующий фрагмент текста по шаблонам из обучения.",
        "Разделите задачу на шаги: цель → черновик → критика → улучшенная версия.",
        "Для документов запрещайте модели добавлять факты вне исходного текста — это снижает [[галлюцинация|галлюцинации]].",
        "Сравните два ответа модели и отметьте, где они расходятся — это точки для проверки человеком.",
        "Укажите роль («ты — редактор»), тон и длину ответа — качество заметно растёт.",
        "Попросите модель перечислить допущения и риски отдельным списком.",
        "Используйте пример «хорошо/плохо», чтобы задать уровень качества.",
        "Фиксируйте удачные промты в личной библиотеке — это ваш главный актив.",
    )

    private val MICRO_EXAMPLES: List<String> = listOf(
        "Вы просите ИИ составить план презентации. Сначала указываете аудиторию и цель, затем просите план из 5 слайдов — ответ становится пригодным к работе.",
        "Нужно резюме длинного отчёта: загружаете текст, просите «только факты из документа» и «3 риска» — снижается риск выдуманных деталей.",
        "Учебная задача: попросите объяснить тему аналогией, затем попросите 3 вопроса для самопроверки.",
        "Рабочее письмо: задайте тон (официальный/дружелюбный), длину и запрет на клише — черновик ближе к нужному стилю.",
        "Сравнение вариантов: попросите две версии ответа (краткая и подробная) и критерии выбора.",
        "Исследование: попросите список гипотез, а не «истину» — вы остаётесь автором решения.",
        "Таблица: попросите колонки «шаг | ответственный | риск | проверка».",
        "Итерация: «улучши предыдущий ответ, сохранив факты, усилив структуру».",
        "Ограничение: «не более 120 слов, без англицизмов, без эмодзи».",
        "Проверка: «отметь 3 утверждения, которые нужно перепроверить вне ИИ».",
    )

    private val MICRO_MISTAKES: List<String> = listOf(
        "Частая ошибка: слишком общий запрос без контекста. ИИ заполнит пробелы фантазией.",
        "Не передавайте пароли, персональные данные и коммерческие тайны в облачные чаты.",
        "Не путайте уверенный тон ответа с достоверностью — проверяйте факты отдельно.",
        "Один промт «сделай всё» редко работает. Лучше 2–3 шага с промежуточной проверкой.",
        "Не копируйте ответ в важный документ без вычитки и адаптации под вашу аудиторию.",
        "Игнорирование формата: если нужна таблица — попросите таблицу явно.",
        "Забывают указать язык и уровень детализации (новичок / эксперт).",
        "Используют ИИ для юридических и медицинских решений без эксперта — высокий риск.",
        "Не сохраняют удачные промты — приходится изобретать заново.",
        "Сравнивают модели без одинакового промта — выводы о «лучшей модели» некорректны.",
    )

    private val MICRO_DEEP_DIVES: List<String> = listOf(
        "Структура «роль → задача → контекст → формат → критерии → ограничения» покрывает 80% бытовых сценариев.",
        "Температура влияет на креативность: ниже — стабильнее, выше — разнообразнее. Для фактов держите ниже.",
        "Контекстное окно ограничено: длинные документы лучше дробить и ссылаться на части.",
        "Итеративный диалог дешевле, чем попытка получить идеал с первого сообщения.",
        "Для команд полезна общая библиотека промтов с пометкой, где сработало.",
        "RAG и поиск по документам снижают галлюцинации, если источники актуальны.",
        "Агентные сценарии требуют подтверждения пользователя на рискованных шагах.",
        "Этика: указывайте авторство, не выдавайте сгенерированный текст за чужой труд без проверки.",
        "Метрики качества: полнота, точность, соответствие формату, отсутствие лишних фактов.",
        "Связывайте урок с KPI: что изменится в работе/учёбе после применения.",
    )

    private val MICRO_FOCUS_TOPICS: List<String> = listOf(
        "понимание термина",
        "пример из жизни",
        "типичная ошибка",
        "проверка фактов",
        "структура промта",
        "итерация ответа",
        "работа с документом",
        "безопасность данных",
        "этика и границы",
        "итоговая практика",
    )

    private val PRACTICE_STEPS: List<String> = listOf(
        "Сократите ответ модели до 5 пунктов и оцените каждый по шкале 1–5.",
        "Попросите альтернативный вариант решения и сравните с первым.",
        "Добавьте ограничение: «не более 120 слов» и проверьте соблюдение.",
        "Попросите список того, что нужно проверить у человека-эксперта.",
        "Сформулируйте уточняющий вопрос модели, если ответ слишком общий.",
        "Перепишите промт, убрав двусмысленные слова.",
        "Попросите ответ в виде таблицы: задача | шаг | риск | проверка.",
        "Добавьте контекст: кто аудитория и зачем им это нужно.",
        "Попросите пример «как НЕ надо делать» и исправьте его.",
        "Сохраните лучший промт в заметки и подпишите, когда его использовать.",
    )

    private val MICRO_QUIZ: List<MicroQuizTemplate> = listOf(
        MicroQuizTemplate(
            "Нужно ли проверять важные ответы ИИ?",
            listOf("Да", "Нет"),
            0,
            "Да — особенно в темах денег, здоровья, права и работы.",
        ),
        MicroQuizTemplate(
            "Промт должен быть…",
            listOf("Коротким и ясным", "Без контекста", "Только на английском"),
            0,
            "Чем яснее контекст и формат, тем полезнее ответ.",
        ),
        MicroQuizTemplate(
            "Галлюцинация — это…",
            listOf("Уверенный, но неверный ответ", "Медленная модель", "Платная функция"),
            0,
            "Модель может звучать убедительно и ошибаться.",
        ),
        MicroQuizTemplate(
            "Что добавить в промт в первую очередь?",
            listOf("Роль и формат ответа", "Случайные эмодзи", "Пароль от почты"),
            0,
            "Роль, задача, формат и критерии качества — база.",
        ),
        MicroQuizTemplate(
            "Можно ли передавать в облако пароли?",
            listOf("Нет", "Да, всегда"),
            0,
            "Пароли и ключи нельзя отправлять в чат-боты.",
        ),
    )

    private data class MicroQuizTemplate(
        val question: String,
        val options: List<String>,
        val answerIndex: Int,
        val explanation: String,
    )
}
