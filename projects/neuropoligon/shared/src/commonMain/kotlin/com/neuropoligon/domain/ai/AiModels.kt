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

package com.neuropoligon.domain.ai

import kotlinx.serialization.Serializable

@Serializable
public enum class AiProvider {
    Anthropic,
    OpenAI,
    DeepSeek,
    Groq,
    Gemini,
    Mistral,
    Local,
}

public data class ProviderCapabilities(
    val supportsStreaming: Boolean = false,
    val supportsFunctionCalling: Boolean = false,
    val supportsVision: Boolean = false,
    val availableOnWeb: Boolean = true,
)

public data class AiMessage(
    val role: String,
    val content: String,
)

public data class AiTool(
    val name: String,
    val description: String,
    val parametersJson: String = "{}",
)

public data class AiRequest(
    val provider: AiProvider,
    val systemPrompt: String = "",
    val messages: List<AiMessage> = emptyList(),
    val temperature: Double = 0.7,
    val topP: Double = 0.9,
    val topK: Int? = null,
    val maxTokens: Int = 512,
    val tools: List<AiTool> = emptyList(),
    val localBaseUrl: String = "http://localhost:11434/v1",
)

public data class AiResponse(
    val text: String,
    val toolCalls: List<String> = emptyList(),
)

public sealed class AiError {
    public data class NoApiKey(val provider: AiProvider) : AiError()
    public data class Auth(val message: String) : AiError()
    public data class Balance(val message: String) : AiError()
    public data class RateLimit(val message: String) : AiError()
    public data class Network(val message: String) : AiError()
    public data class UnsupportedOnPlatform(val provider: AiProvider) : AiError()
    public data class Provider(val message: String) : AiError()
}

public fun AiError.userMessage(): String = when (this) {
    is AiError.NoApiKey -> "Добавьте API-ключ для ${provider.name} в настройках."
    is AiError.Auth -> "Ошибка авторизации: $message. Проверьте ключ."
    is AiError.Balance -> "Недостаточно средств на балансе провайдера."
    is AiError.RateLimit -> "Превышен лимит запросов. Подождите и повторите."
    is AiError.Network -> "Нет сети или сервер недоступен: $message"
    is AiError.UnsupportedOnPlatform -> "${provider.name} недоступен на этой платформе (например, CORS в браузере)."
    is AiError.Provider -> message
}

public interface AiClient {
    public suspend fun complete(request: AiRequest): Result<AiResponse>
    public fun capabilities(provider: AiProvider): ProviderCapabilities
    public suspend fun isProviderConfigured(provider: AiProvider): Boolean
}

public object AiCapabilities {
    private val map: Map<AiProvider, ProviderCapabilities> = mapOf(
        AiProvider.Anthropic to ProviderCapabilities(
            supportsStreaming = true,
            supportsFunctionCalling = true,
            availableOnWeb = true,
        ),
        AiProvider.OpenAI to ProviderCapabilities(
            supportsStreaming = true,
            supportsFunctionCalling = true,
            availableOnWeb = true,
        ),
        AiProvider.DeepSeek to ProviderCapabilities(
            supportsStreaming = true,
            availableOnWeb = false,
        ),
        AiProvider.Groq to ProviderCapabilities(true, true, availableOnWeb = true),
        AiProvider.Gemini to ProviderCapabilities(true, availableOnWeb = true),
        AiProvider.Mistral to ProviderCapabilities(true, availableOnWeb = true),
        AiProvider.Local to ProviderCapabilities(true, true, availableOnWeb = true),
    )

    public fun of(provider: AiProvider): ProviderCapabilities =
        map[provider] ?: ProviderCapabilities()
}
