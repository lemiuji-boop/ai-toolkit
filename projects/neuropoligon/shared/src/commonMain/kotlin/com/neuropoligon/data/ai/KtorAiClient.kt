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

package com.neuropoligon.data.ai

import com.neuropoligon.domain.ai.AiCapabilities
import com.neuropoligon.domain.ai.AiClient
import com.neuropoligon.domain.ai.AiError
import com.neuropoligon.domain.ai.AiProvider
import com.neuropoligon.domain.ai.AiRequest
import com.neuropoligon.domain.ai.AiResponse
import com.neuropoligon.domain.ai.ProviderCapabilities
import com.neuropoligon.domain.ai.userMessage
import io.ktor.http.HttpStatusCode
import com.neuropoligon.platform.SecureStorage
import com.neuropoligon.platform.isWebPlatform
import com.neuropoligon.platform.createPlatformHttpClient
import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.HttpResponse
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

public class KtorAiClient(
    private val secureStorage: SecureStorage,
    private val httpClient: HttpClient,
) : AiClient {
    override fun capabilities(provider: AiProvider): ProviderCapabilities = AiCapabilities.of(provider)

    override suspend fun isProviderConfigured(provider: AiProvider): Boolean =
        when (provider) {
            AiProvider.Local -> true
            else -> secureStorage.get(secureStorageKey(provider))?.isNotBlank() == true
        }

    override suspend fun complete(request: AiRequest): Result<AiResponse> {
        if (!capabilities(request.provider).availableOnWeb && isWebPlatform()) {
            return Result.failure(aiException(AiError.UnsupportedOnPlatform(request.provider)))
        }
        if (request.provider != AiProvider.Local && !isProviderConfigured(request.provider)) {
            return Result.failure(aiException(AiError.NoApiKey(request.provider)))
        }
        return runCatching {
            when (request.provider) {
                AiProvider.OpenAI, AiProvider.Local, AiProvider.Groq, AiProvider.DeepSeek, AiProvider.Mistral ->
                    completeOpenAiCompatible(request)
                AiProvider.Anthropic -> completeAnthropic(request)
                AiProvider.Gemini -> completeGemini(request)
            }
        }.fold(
            onSuccess = { Result.success(it) },
            onFailure = { err -> Result.failure(err as? Exception ?: aiException(mapThrowable(err))) },
        )
    }

    private suspend fun completeOpenAiCompatible(request: AiRequest): AiResponse {
        val key = secureStorage.get(secureStorageKey(request.provider)).orEmpty()
        val baseUrl = when (request.provider) {
            AiProvider.Local -> request.localBaseUrl.trimEnd('/')
            AiProvider.Groq -> "https://api.groq.com/openai/v1"
            AiProvider.DeepSeek -> "https://api.deepseek.com/v1"
            AiProvider.Mistral -> "https://api.mistral.ai/v1"
            else -> "https://api.openai.com/v1"
        }
        val body = OpenAiChatRequest(
            model = when (request.provider) {
                AiProvider.Local -> "llama3.2"
                AiProvider.Groq -> "llama-3.1-8b-instant"
                AiProvider.DeepSeek -> "deepseek-chat"
                AiProvider.Mistral -> "mistral-small-latest"
                else -> "gpt-4o-mini"
            },
            messages = buildList {
                if (request.systemPrompt.isNotBlank()) add(OpenAiMessage("system", request.systemPrompt))
                request.messages.forEach { add(OpenAiMessage(it.role, it.content)) }
            },
            temperature = request.temperature,
            topP = request.topP,
            maxTokens = request.maxTokens,
        )
        val response: HttpResponse = httpClient.post("$baseUrl/chat/completions") {
            if (request.provider != AiProvider.Local) {
                header("Authorization", "Bearer $key")
            }
            setBody(body)
        }
        if (!response.status.isSuccess()) throw aiException(mapHttpError(response.status.value, response.body<String>()))
        val parsed = response.body<OpenAiChatResponse>()
        val text = parsed.choices.firstOrNull()?.message?.content ?: ""
        return AiResponse(text)
    }

    private suspend fun completeAnthropic(request: AiRequest): AiResponse {
        val key = secureStorage.get(secureStorageKey(AiProvider.Anthropic)).orEmpty()
        val body = AnthropicRequest(
            model = "claude-3-5-haiku-latest",
            maxTokens = request.maxTokens,
            system = request.systemPrompt.takeIf { it.isNotBlank() },
            messages = request.messages.map { AnthropicMessage(it.role, it.content) },
            temperature = request.temperature,
        )
        val response: HttpResponse = httpClient.post("https://api.anthropic.com/v1/messages") {
            header("x-api-key", key)
            header("anthropic-version", "2023-06-01")
            if (isWebPlatform()) {
                header("anthropic-dangerous-direct-browser-access", "true")
            }
            setBody(body)
        }
        if (!response.status.isSuccess()) throw aiException(mapHttpError(response.status.value, response.body<String>()))
        val parsed = response.body<AnthropicResponse>()
        val text = parsed.content.firstOrNull()?.text ?: ""
        return AiResponse(text)
    }

    private suspend fun completeGemini(request: AiRequest): AiResponse {
        val key = secureStorage.get(secureStorageKey(AiProvider.Gemini)).orEmpty()
        val prompt = (listOfNotNull(request.systemPrompt.takeIf { it.isNotBlank() }) +
            request.messages.map { "${it.role}: ${it.content}" }).joinToString("\n")
        val response: HttpResponse = httpClient.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$key",
        ) {
            setBody(GeminiRequest(contents = listOf(GeminiContent(parts = listOf(GeminiPart(prompt))))))
        }
        if (!response.status.isSuccess()) throw aiException(mapHttpError(response.status.value, response.body<String>()))
        val parsed = response.body<GeminiResponse>()
        val text = parsed.candidates.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: ""
        return AiResponse(text)
    }

    private fun secureStorageKey(provider: AiProvider): String = "api_key_${provider.name}"

    private fun mapHttpError(code: Int, body: String): AiError = when (code) {
        401, 403 -> AiError.Auth(body.take(200))
        402 -> AiError.Balance("Проверьте баланс провайдера.")
        429 -> AiError.RateLimit("Слишком много запросов.")
        else -> AiError.Provider("HTTP $code: ${body.take(200)}")
    }

    private fun mapThrowable(t: Throwable): AiError = when (t) {
        is AiException -> t.error
        else -> AiError.Network(t.message ?: "Сетевая ошибка")
    }
}

internal class AiException(val error: AiError) : Exception(error.userMessage())

private fun aiException(error: AiError): AiException = AiException(error)

private fun HttpStatusCode.isSuccess(): Boolean = value in 200..299

public class AiGateway(private val client: AiClient) {
    public suspend fun complete(request: AiRequest): Result<AiResponse> = client.complete(request)
}

@Serializable
private data class OpenAiChatRequest(
    val model: String,
    val messages: List<OpenAiMessage>,
    val temperature: Double,
    @SerialName("top_p") val topP: Double,
    @SerialName("max_tokens") val maxTokens: Int,
)

@Serializable
private data class OpenAiMessage(val role: String, val content: String)

@Serializable
private data class OpenAiChatResponse(val choices: List<OpenAiChoice> = emptyList())

@Serializable
private data class OpenAiChoice(val message: OpenAiMessage)

@Serializable
private data class AnthropicRequest(
    val model: String,
    @SerialName("max_tokens") val maxTokens: Int,
    val system: String? = null,
    val messages: List<AnthropicMessage>,
    val temperature: Double,
)

@Serializable
private data class AnthropicMessage(val role: String, val content: String)

@Serializable
private data class AnthropicResponse(val content: List<AnthropicContentPart> = emptyList())

@Serializable
private data class AnthropicContentPart(val text: String)

@Serializable
private data class GeminiRequest(val contents: List<GeminiContent>)

@Serializable
private data class GeminiContent(val parts: List<GeminiPart>)

@Serializable
private data class GeminiPart(val text: String)

@Serializable
private data class GeminiResponse(val candidates: List<GeminiCandidate> = emptyList())

@Serializable
private data class GeminiCandidate(val content: GeminiContent)
