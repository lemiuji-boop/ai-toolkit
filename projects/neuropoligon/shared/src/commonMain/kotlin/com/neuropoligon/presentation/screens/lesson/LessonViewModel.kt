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

package com.neuropoligon.presentation.screens.lesson

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.neuropoligon.domain.ai.AiClient
import com.neuropoligon.domain.ai.AiError
import com.neuropoligon.domain.ai.AiMessage
import com.neuropoligon.domain.ai.AiProvider
import com.neuropoligon.domain.ai.AiRequest
import com.neuropoligon.domain.ai.userMessage
import com.neuropoligon.domain.challenge.ChallengeEvaluator
import com.neuropoligon.domain.content.Block
import com.neuropoligon.domain.content.Challenge
import com.neuropoligon.domain.content.ContentEngine
import com.neuropoligon.domain.content.ContentRepository
import com.neuropoligon.domain.content.GlossaryEntry
import com.neuropoligon.domain.content.GlossaryRepository
import com.neuropoligon.domain.content.Module
import com.neuropoligon.domain.content.Track
import com.neuropoligon.domain.progress.ProgressRepository
import com.neuropoligon.domain.content.SandboxConfig
import com.neuropoligon.domain.content.SandboxType
import com.neuropoligon.domain.sandbox.SandboxResult
import com.neuropoligon.domain.sandbox.SandboxRuntime
import com.neuropoligon.domain.sandbox.SandboxUserInput
import com.neuropoligon.domain.settings.LessonReaderSettings
import com.neuropoligon.domain.settings.ReaderColorTone
import com.neuropoligon.domain.settings.SettingsRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

public enum class LessonPage {
    Theory,
    Practice,
    Quiz,
}

public enum class AiConnectionStatus {
    Unknown,
    Ready,
    NoApiKey,
    Generating,
    Error,
}

public data class LessonListItem(
    val moduleId: String,
    val title: String,
    val chapterTitle: String?,
    val isCurrent: Boolean,
)

public class LessonViewModel(
    private val contentRepository: ContentRepository,
    private val contentEngine: ContentEngine,
    private val settingsRepository: SettingsRepository,
    private val progressRepository: ProgressRepository,
    private val glossaryRepository: GlossaryRepository,
    private val aiClient: AiClient,
    private val sandboxRuntime: SandboxRuntime,
    private val challengeEvaluator: ChallengeEvaluator,
) : ViewModel() {
    private val _module = MutableStateFlow<Module?>(null)
    public val module: StateFlow<Module?> = _module.asStateFlow()
    private val _glossary = MutableStateFlow<List<GlossaryEntry>>(emptyList())
    public val glossary: StateFlow<List<GlossaryEntry>> = _glossary.asStateFlow()
    private val _nextModuleId = MutableStateFlow<String?>(null)
    public val nextModuleId: StateFlow<String?> = _nextModuleId.asStateFlow()
    private val _courseProgress = MutableStateFlow(0f)
    public val courseProgress: StateFlow<Float> = _courseProgress.asStateFlow()
    private val _lessonIndex = MutableStateFlow(0)
    public val lessonIndex: StateFlow<Int> = _lessonIndex.asStateFlow()
    private val _totalLessons = MutableStateFlow(0)
    public val totalLessons: StateFlow<Int> = _totalLessons.asStateFlow()
    private val _uiMessage = MutableStateFlow<String?>(null)
    public val uiMessage: StateFlow<String?> = _uiMessage.asStateFlow()
    private val _page = MutableStateFlow(LessonPage.Theory)
    public val page: StateFlow<LessonPage> = _page.asStateFlow()
    private val _lessonItems = MutableStateFlow<List<LessonListItem>>(emptyList())
    public val lessonItems: StateFlow<List<LessonListItem>> = _lessonItems.asStateFlow()
    private val _readerSettings = MutableStateFlow(LessonReaderSettings())
    public val readerSettings: StateFlow<LessonReaderSettings> = _readerSettings.asStateFlow()
    private val _theoryMarkdown = MutableStateFlow("")
    public val theoryMarkdown: StateFlow<String> = _theoryMarkdown.asStateFlow()
    private val _practicePrompt = MutableStateFlow("")
    public val practicePrompt: StateFlow<String> = _practicePrompt.asStateFlow()
    private val _generatedText = MutableStateFlow("")
    public val generatedText: StateFlow<String> = _generatedText.asStateFlow()
    private val _aiStatus = MutableStateFlow(AiConnectionStatus.Unknown)
    public val aiStatus: StateFlow<AiConnectionStatus> = _aiStatus.asStateFlow()
    private val _scrollToTopTick = MutableStateFlow(0)
    public val scrollToTopTick: StateFlow<Int> = _scrollToTopTick.asStateFlow()
    private val _transitionTick = MutableStateFlow(0)
    public val transitionTick: StateFlow<Int> = _transitionTick.asStateFlow()
    private val _sandboxResult = MutableStateFlow<SandboxResult?>(null)
    public val sandboxResult: StateFlow<SandboxResult?> = _sandboxResult.asStateFlow()
    private val _challengeFeedback = MutableStateFlow<String?>(null)
    public val challengeFeedback: StateFlow<String?> = _challengeFeedback.asStateFlow()
    private val _note = MutableStateFlow("")
    public val note: StateFlow<String> = _note.asStateFlow()
    private val _bookmarked = MutableStateFlow(false)
    public val bookmarked: StateFlow<Boolean> = _bookmarked.asStateFlow()

    private var trackId: String = ""
    private var moduleId: String = ""
    private var currentTrack: Track? = null

    public fun load(trackId: String, moduleId: String) {
        this.trackId = trackId
        this.moduleId = moduleId
        viewModelScope.launch {
            contentRepository.getTracks()
            settingsRepository.getLessonReaderSettings().let { _readerSettings.value = it }
            glossaryRepository.getEntries().let { _glossary.value = it }
            val tracks = contentEngine.observeFilteredTracks().first()
            currentTrack = tracks.firstOrNull { it.id == trackId }
            applyModule(currentTrack?.modules?.firstOrNull { it.id == moduleId })
            loadPersonalData()
            refreshAiStatus()
        }
    }

    public fun openLesson(moduleId: String) {
        if (moduleId == this.moduleId) return
        this.moduleId = moduleId
        viewModelScope.launch {
            applyModule(currentTrack?.modules?.firstOrNull { it.id == moduleId })
            _transitionTick.value += 1
        }
    }

    public fun setPage(page: LessonPage) {
        _page.value = page
        _transitionTick.value += 1
    }

    public fun scrollToTop() {
        _scrollToTopTick.value += 1
    }

    public fun updateNote(value: String) { _note.value = value }

    public fun saveNote() { viewModelScope.launch { progressRepository.saveNote("note-", moduleId, _note.value.trim()); showMessage("Заметка сохранена") } }

    public fun toggleBookmark() { viewModelScope.launch { if (_bookmarked.value) progressRepository.deleteNote("bookmark-") else progressRepository.saveNote("bookmark-", moduleId, "bookmark"); _bookmarked.value = !_bookmarked.value } }

    private suspend fun loadPersonalData() { val notes = progressRepository.observeNotes().first(); _note.value = notes.firstOrNull { it.noteId == "note-" }?.text.orEmpty(); _bookmarked.value = notes.any { it.noteId == "bookmark-" } }

    public fun updatePracticePrompt(value: String) {
        _practicePrompt.value = value
    }

    public fun updateReaderFontScale(scale: Float) {
        updateReader { it.copy(fontScale = scale.coerceIn(0.85f, 1.45f)) }
    }

    public fun updateReaderTemperature(value: Double) {
        updateReader { it.copy(aiTemperature = value.coerceIn(0.0, 1.5)) }
    }

    public fun updateReaderTone(tone: ReaderColorTone) {
        updateReader { it.copy(colorTone = tone) }
    }

    public fun generateFromPrompt() {
        val prompt = _practicePrompt.value.trim()
        if (prompt.isBlank()) {
            showMessage("Введите промт")
            return
        }
        viewModelScope.launch {
            val provider = resolveProvider() ?: run {
                _aiStatus.value = AiConnectionStatus.NoApiKey
                showMessage("Добавьте API-ключ в настройках")
                return@launch
            }
            _aiStatus.value = AiConnectionStatus.Generating
            val settings = _readerSettings.value
            val result = aiClient.complete(
                AiRequest(
                    provider = provider,
                    systemPrompt = "Ты — дружелюбный наставник по ИИ. Отвечай на русском, структурированно.",
                    messages = listOf(AiMessage("user", prompt)),
                    temperature = settings.aiTemperature,
                    maxTokens = 900,
                ),
            )
            result.fold(
                onSuccess = {
                    _generatedText.value = it.text
                    _aiStatus.value = AiConnectionStatus.Ready
                },
                onFailure = { e ->
                    val msg = (e as? AiError)?.userMessage() ?: e.message ?: "Ошибка генерации"
                    _generatedText.value = msg
                    _aiStatus.value = AiConnectionStatus.Error
                },
            )
        }
    }

    public fun completeBlock(blockId: String) {
        viewModelScope.launch {
            progressRepository.markBlockCompleted(blockId, trackId, moduleId)
        }
    }

    public fun completeTheory() {
        viewModelScope.launch {
            progressRepository.markBlockCompleted("theory-$moduleId", trackId, moduleId)
            setPage(LessonPage.Practice)
        }
    }

    public fun completePractice() {
        viewModelScope.launch {
            progressRepository.markBlockCompleted("practice-$moduleId", trackId, moduleId)
            setPage(LessonPage.Quiz)
        }
    }

    public fun runSandbox(type: SandboxType, config: SandboxConfig, input: SandboxUserInput) {
        viewModelScope.launch {
            _sandboxResult.value = sandboxRuntime.run(type, config, input)
        }
    }

    public fun evaluateChallenge(challenge: Challenge, params: Map<String, Double>) {
        val evaluation = challengeEvaluator.evaluate(challenge, params)
        _challengeFeedback.value = evaluation.feedback
        if (evaluation.passed) {
            viewModelScope.launch {
                progressRepository.markBlockCompleted("challenge-${challenge.id}", trackId, moduleId)
            }
        }
    }

    public fun skipQuiz() {
        viewModelScope.launch {
            progressRepository.markBlockCompleted("quiz-skipped-$moduleId", trackId, moduleId)
            showMessage("Тест пропущен")
        }
    }

    public fun completeQuiz() {
        viewModelScope.launch {
            progressRepository.markBlockCompleted("quiz-$moduleId", trackId, moduleId)
        }
    }

    public suspend fun markdownFor(block: Block.Explanation): String {
        val level = settingsRepository.getDifficultyLevel()
        return contentEngine.resolveMarkdown(block, level)
    }

    public fun showMessage(message: String) {
        _uiMessage.value = message
    }

    public fun clearMessage() {
        _uiMessage.value = null
    }

    private suspend fun applyModule(module: Module?) {
        _module.value = module
        _page.value = LessonPage.Theory
        _generatedText.value = ""
        updateModuleProgress()
        buildLessonList()
        module?.let { m ->
            val explanation = m.blocks.filterIsInstance<Block.Explanation>().firstOrNull()
            _theoryMarkdown.value = explanation?.let { markdownFor(it) }.orEmpty()
            _practicePrompt.value = m.blocks.filterIsInstance<Block.Practice>().firstOrNull()?.prompt.orEmpty()
        }
    }

    private suspend fun refreshAiStatus() {
        _aiStatus.value = if (resolveProvider() != null) AiConnectionStatus.Ready else AiConnectionStatus.NoApiKey
    }

    private suspend fun resolveProvider(): AiProvider? =
        AiProvider.entries.firstOrNull { aiClient.isProviderConfigured(it) }

    private fun updateReader(transform: (LessonReaderSettings) -> LessonReaderSettings) {
        val next = transform(_readerSettings.value)
        _readerSettings.value = next
        viewModelScope.launch { settingsRepository.setLessonReaderSettings(next) }
    }

    private suspend fun buildLessonList() {
        val modules = currentTrack?.modules.orEmpty()
        _lessonItems.value = modules.map { m ->
            LessonListItem(
                moduleId = m.id,
                title = m.title,
                chapterTitle = m.chapterTitle,
                isCurrent = m.id == moduleId,
            )
        }
    }

    private suspend fun updateModuleProgress() {
        val modules = currentTrack?.modules.orEmpty()
        if (modules.isEmpty()) {
            _courseProgress.value = 0f
            _nextModuleId.value = null
            _lessonIndex.value = 0
            _totalLessons.value = 0
            return
        }
        val currentIndex = modules.indexOfFirst { it.id == moduleId }.coerceAtLeast(0)
        _nextModuleId.value = modules.getOrNull(currentIndex + 1)?.id
        _courseProgress.value = (currentIndex + 1).toFloat() / modules.size.toFloat()
        _lessonIndex.value = currentIndex + 1
        _totalLessons.value = modules.size
    }
}
