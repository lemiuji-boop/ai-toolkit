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

package com.neuropoligon.domain.sandbox

import com.neuropoligon.domain.ai.AiClient
import com.neuropoligon.domain.ai.AiError
import com.neuropoligon.domain.ai.userMessage
import com.neuropoligon.domain.ai.AiMessage
import com.neuropoligon.domain.ai.AiProvider
import com.neuropoligon.domain.ai.AiRequest
import com.neuropoligon.domain.ai.AiTool
import com.neuropoligon.domain.content.SandboxConfig
import com.neuropoligon.domain.content.SandboxType
import com.neuropoligon.foundations.EmbeddingStore
import com.neuropoligon.foundations.SimpleBpeTokenizer
import com.neuropoligon.platform.PlatformInfo
import com.neuropoligon.platform.isWebPlatform
import kotlin.math.min

/**
 * Исполнение песочниц: офлайн — чистые функции, AI — через AiClient.
 */
public class SandboxRuntime(
    private val tokenizer: SimpleBpeTokenizer,
    private val embeddingStore: EmbeddingStore,
    private val aiClient: AiClient,
    private val platformInfo: PlatformInfo = PlatformInfo(),
) {
    public suspend fun run(
        type: SandboxType,
        config: SandboxConfig,
        input: SandboxUserInput,
    ): SandboxResult = when (type) {
        SandboxType.Tokenizer -> runTokenizer(input)
        SandboxType.Embedding -> runEmbedding(input)
        SandboxType.Temperature -> runTemperature(config, input)
        SandboxType.TopP -> runTopP(config, input)
        SandboxType.SystemPrompt -> runSystemPrompt(config, input)
        SandboxType.Rag -> runRag(config, input)
        SandboxType.FunctionCalling -> runFunctionCalling(config, input)
        SandboxType.Agent -> runAgent(config, input)
    }

    private fun runTokenizer(input: SandboxUserInput): SandboxResult.Tokenizer {
        val text = input.text.ifBlank { "Привет, это пример токенизации!" }
        return SandboxResult.Tokenizer(tokenizer.tokenize(text))
    }

    private fun runEmbedding(input: SandboxUserInput): SandboxResult.Embedding {
        val word = input.text.ifBlank { "кот" }
        val vector = embeddingStore.embed(word)
        return SandboxResult.Embedding(
            word = word,
            vector = vector,
            neighbors = embeddingStore.nearest(word, 8),
            allPoints = embeddingStore.allPoints(),
        )
    }

    private suspend fun runTemperature(config: SandboxConfig, input: SandboxUserInput): SandboxResult {
        val prompt = input.text.ifBlank { config.prompt.ifBlank { "Расскажи коротко про токены." } }
        return compareAi(
            prompt = prompt,
            values = listOf(0.1, 0.7, 1.2),
            input = input,
            labelFn = { temp, _ -> "t=$temp" },
        )
    }

    private suspend fun runTopP(config: SandboxConfig, input: SandboxUserInput): SandboxResult {
        val prompt = input.text.ifBlank { config.prompt.ifBlank { "Придумай 3 слова про ИИ." } }
        return compareAi(
            prompt = prompt,
            values = listOf(0.3, 0.7, 0.95),
            input = input,
            labelFn = { _, topP -> "topP=$topP" },
            useTopP = true,
        )
    }

    private suspend fun runSystemPrompt(config: SandboxConfig, input: SandboxUserInput): SandboxResult {
        val prompt = input.text.ifBlank { "Объясни, что такое RAG." }
        val provider = resolveProvider(input)
        if (!aiClient.isProviderConfigured(provider)) {
            return offlineSystemPromptDemo(prompt)
        }
        val variants = listOf(
            "Строгий эксперт" to "Ты — строгий преподаватель. Отвечай кратко и по делу.",
            "Дружелюбный наставник" to "Ты — дружелюбный наставник. Объясняй простыми аналогиями.",
        )
        val results = mutableListOf<AiVariant>()
        for ((label, system) in variants) {
            val response = aiClient.complete(
                AiRequest(
                    provider = provider,
                    systemPrompt = input.systemPrompt ?: system,
                    messages = listOf(AiMessage("user", prompt)),
                    temperature = 0.7,
                ),
            )
            response.fold(
                onSuccess = { results.add(AiVariant(label, it.text)) },
                onFailure = { return it.toSandboxResult(prompt) },
            )
        }
        return SandboxResult.AiComparison(prompt, results)
    }

    private suspend fun runRag(config: SandboxConfig, input: SandboxUserInput): SandboxResult.Rag {
        val query = input.text.ifBlank { "Что такое токен?" }
        val docs = config.documents.ifEmpty {
            listOf(
                "Токен — минимальная единица текста для модели.",
                "Эмбеддинг — числовое представление смысла слова.",
                "Температура управляет случайностью генерации.",
            )
        }
        val chunks = docs.map { doc ->
            val score = doc.lowercase().split(" ").count { query.lowercase().contains(it) }.toDouble()
            ScoredChunk(doc, score)
        }.sortedByDescending { it.score }
        val context = chunks.take(2).joinToString("\n") { it.text }
        val provider = resolveProvider(input)
        if (!aiClient.isProviderConfigured(provider)) {
            return SandboxResult.Rag(
                chunks = chunks,
                answerWithContext = null,
                answerWithoutContext = null,
                degradationMessage = AiError.NoApiKey(provider).userMessage(),
            )
        }
        val withCtx = aiClient.complete(
            AiRequest(
                provider = provider,
                systemPrompt = "Отвечай только по контексту.\nКонтекст:\n$context",
                messages = listOf(AiMessage("user", query)),
                temperature = 0.3,
            ),
        )
        val without = aiClient.complete(
            AiRequest(
                provider = provider,
                messages = listOf(AiMessage("user", query)),
                temperature = 0.3,
            ),
        )
        return SandboxResult.Rag(
            chunks = chunks,
            answerWithContext = withCtx.getOrNull()?.text,
            answerWithoutContext = without.getOrNull()?.text,
            degradationMessage = withCtx.exceptionOrNull()?.let { (it as? Exception)?.message },
        )
    }

    private suspend fun runFunctionCalling(config: SandboxConfig, input: SandboxUserInput): SandboxResult.FunctionCalling {
        val provider = resolveProvider(input)
        if (!aiClient.isProviderConfigured(provider)) {
            return SandboxResult.FunctionCalling(
                steps = listOf("Нет API-ключа — показан демо-цикл."),
                finalAnswer = "Демо: get_weather(city=Москва) → +5°C, облачно",
                degradationMessage = AiError.NoApiKey(provider).userMessage(),
            )
        }
        val tool = AiTool("get_weather", "Получить погоду для города")
        val response = aiClient.complete(
            AiRequest(
                provider = provider,
                systemPrompt = "Если нужна погода — опиши вызов инструмента get_weather.",
                messages = listOf(AiMessage("user", input.text.ifBlank { "Какая погода в Москве?" })),
                tools = listOf(tool),
                temperature = 0.2,
            ),
        )
        return response.fold(
            onSuccess = {
                SandboxResult.FunctionCalling(
                    steps = listOf(
                        "1. Запрос пользователя",
                        "2. Модель запросила tool: get_weather",
                        "3. Мок-инструмент вернул данные",
                        "4. Финальный ответ",
                    ),
                    finalAnswer = it.text,
                )
            },
            onFailure = { SandboxResult.FunctionCalling(emptyList(), null, it.message) },
        )
    }

    private suspend fun runAgent(config: SandboxConfig, input: SandboxUserInput): SandboxResult.Agent {
        val provider = resolveProvider(input)
        if (!aiClient.isProviderConfigured(provider)) {
            return SandboxResult.Agent(
                steps = listOf(
                    "Thought: нужен план",
                    "Action: search_docs",
                    "Observation: найдено 2 фрагмента",
                    "Answer: демо без ключа",
                ),
                finalAnswer = "Демо ReAct-цикл без сети.",
                degradationMessage = AiError.NoApiKey(provider).userMessage(),
            )
        }
        val response = aiClient.complete(
            AiRequest(
                provider = provider,
                systemPrompt = "Ты агент ReAct: Thought → Action → Observation → Answer. Кратко.",
                messages = listOf(AiMessage("user", input.text.ifBlank { "Найди определение токена." })),
                temperature = 0.4,
            ),
        )
        return response.fold(
            onSuccess = {
                SandboxResult.Agent(
                    steps = it.text.lines().filter { line -> line.isNotBlank() },
                    finalAnswer = it.text,
                )
            },
            onFailure = { SandboxResult.Agent(emptyList(), null, it.message) },
        )
    }

    private suspend fun compareAi(
        prompt: String,
        values: List<Double>,
        input: SandboxUserInput,
        labelFn: (Double, Double) -> String,
        useTopP: Boolean = false,
    ): SandboxResult {
        val provider = resolveProvider(input)
        if (!aiClient.isProviderConfigured(provider)) {
            return SandboxResult.AiComparison(
                prompt = prompt,
                variants = emptyList(),
                degradationMessage = AiError.NoApiKey(provider).userMessage(),
            )
        }
        val results = mutableListOf<AiVariant>()
        for (value in values) {
            val request = AiRequest(
                provider = provider,
                messages = listOf(AiMessage("user", prompt)),
                temperature = if (useTopP) input.temperature ?: 0.7 else value,
                topP = if (useTopP) value else input.topP ?: 0.9,
            )
            val response = aiClient.complete(request)
            response.fold(
                onSuccess = { results.add(AiVariant(labelFn(value, value), it.text)) },
                onFailure = { return it.toSandboxResult(prompt) },
            )
        }
        return SandboxResult.AiComparison(prompt, results)
    }

    private fun resolveProvider(input: SandboxUserInput): AiProvider {
        val name = input.selectedProvider
        return AiProvider.entries.firstOrNull { it.name.equals(name, ignoreCase = true) }
            ?: AiProvider.OpenAI
    }

    private fun Result<*>.toSandboxResult(prompt: String): SandboxResult {
        val error = exceptionOrNull()
        val message = error?.message ?: "Неизвестная ошибка"
        return SandboxResult.AiComparison(prompt, emptyList(), message)
    }

    private fun Throwable.toSandboxResult(prompt: String): SandboxResult =
        SandboxResult.AiComparison(prompt, emptyList(), message)

    /** Офлайн-демо без API-ключа: два стиля ответа по шаблону. */
    private fun offlineSystemPromptDemo(prompt: String): SandboxResult.AiComparison =
        SandboxResult.AiComparison(
            prompt = prompt,
            variants = listOf(
                AiVariant(
                    "Строгий эксперт (демо)",
                    "Кратко: $prompt\n\n" +
                        "• Суть: ИИ строит ответ по шаблонам обучения.\n" +
                        "• Риск: проверьте факты вручную.\n" +
                        "• Совет: добавьте формат и критерии качества в промт.",
                ),
                AiVariant(
                    "Наставник (демо)",
                    "Представьте, что объясняете другу: $prompt\n\n" +
                        "Простая аналогия: модель — автодополнение на стероидах.\n" +
                        "Шаг: перепишите вопрос с ролью «ты — учитель» и лимитом 5 пунктов.",
                ),
            ),
            degradationMessage = "Демо без API-ключа. Добавьте ключ в Настройках для живых ответов.",
        )
}

private fun PlatformInfo(): com.neuropoligon.platform.PlatformInfo =
    com.neuropoligon.platform.PlatformInfo(isWeb = isWebPlatform())
