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

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.neuropoligon.domain.content.Block
import com.neuropoligon.domain.content.ChallengeCriterion
import com.neuropoligon.domain.settings.ReaderColorTone
import com.neuropoligon.platform.copyToClipboard
import com.neuropoligon.presentation.lesson.LessonRichMarkdown
import com.neuropoligon.presentation.lesson.QuizBlockView
import com.neuropoligon.presentation.lesson.readerPalette
import com.neuropoligon.presentation.sandbox.SandboxResultView
import com.neuropoligon.domain.content.SandboxConfig
import com.neuropoligon.domain.content.SandboxType
import com.neuropoligon.domain.sandbox.SandboxUserInput
import org.koin.compose.viewmodel.koinViewModel

private val drawerWidth = 300.dp
private val drawerAnimMs = 550

@Composable
public fun LessonFlowScreen(
    trackId: String,
    moduleId: String,
    onBack: () -> Unit,
    onNextModule: ((String) -> Unit)? = null,
    viewModel: LessonViewModel = koinViewModel(),
) {
    LaunchedEffect(trackId, moduleId) { viewModel.load(trackId, moduleId) }

    val module by viewModel.module.collectAsState()
    val glossary by viewModel.glossary.collectAsState()
    val page by viewModel.page.collectAsState()
    val readerSettings by viewModel.readerSettings.collectAsState()
    val theoryMarkdown by viewModel.theoryMarkdown.collectAsState()
    val practicePrompt by viewModel.practicePrompt.collectAsState()
    val generatedText by viewModel.generatedText.collectAsState()
    val aiStatus by viewModel.aiStatus.collectAsState()
    val lessonItems by viewModel.lessonItems.collectAsState()
    val progress by viewModel.courseProgress.collectAsState()
    val lessonIndex by viewModel.lessonIndex.collectAsState()
    val totalLessons by viewModel.totalLessons.collectAsState()
    val nextModuleId by viewModel.nextModuleId.collectAsState()
    val uiMessage by viewModel.uiMessage.collectAsState()
    val scrollTick by viewModel.scrollToTopTick.collectAsState()
    val transitionTick by viewModel.transitionTick.collectAsState()
    val sandboxResult by viewModel.sandboxResult.collectAsState()
    val challengeFeedback by viewModel.challengeFeedback.collectAsState()
    val note by viewModel.note.collectAsState()
    val bookmarked by viewModel.bookmarked.collectAsState()

    var drawerOpen by remember { mutableStateOf(false) }
    var settingsExpanded by remember { mutableStateOf(false) }
    val snackbarHostState = remember { SnackbarHostState() }
    val scrollState = rememberScrollState()
    val palette = readerPalette(MaterialTheme.colorScheme, readerSettings.colorTone)

    val drawerOffset by animateDpAsState(
        targetValue = if (drawerOpen) 0.dp else -drawerWidth,
        animationSpec = tween(drawerAnimMs),
        label = "drawer-offset",
    )

    LaunchedEffect(uiMessage) {
        uiMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.clearMessage()
        }
    }

    LaunchedEffect(scrollTick, transitionTick, page, moduleId) {
        scrollState.animateScrollTo(0)
    }

    Box(Modifier.fillMaxSize()) {
        Scaffold(
            snackbarHost = { SnackbarHost(snackbarHostState) },
            containerColor = palette.background,
        ) { padding ->
            Column(
                Modifier
                    .fillMaxSize()
                    .padding(padding),
            ) {
                LessonTopBar(
                    onBack = onBack,
                    onMenu = { drawerOpen = true },
                    page = page,
                    onPageSelect = {
                        viewModel.setPage(it)
                        viewModel.scrollToTop()
                    },
                    settingsExpanded = settingsExpanded,
                    onToggleSettings = { settingsExpanded = !settingsExpanded },
                )

                AnimatedVisibility(visible = settingsExpanded) {
                    ReaderSettingsPanel(
                        fontScale = readerSettings.fontScale,
                        temperature = readerSettings.aiTemperature,
                        tone = readerSettings.colorTone,
                        onFontScale = viewModel::updateReaderFontScale,
                        onTemperature = viewModel::updateReaderTemperature,
                        onTone = viewModel::updateReaderTone,
                        palette = palette,
                    )
                }

                if (module == null) {
                    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = palette.accent)
                    }
                    return@Column
                }

                val current = module!!
                LessonHeader(
                    title = current.title,
                    chapter = current.chapterTitle,
                    summary = current.summary,
                    lessonIndex = lessonIndex,
                    totalLessons = totalLessons,
                    durationMinutes = current.durationMinutes,
                    progress = progress,
                    palette = palette,
                )

                HorizontalDivider(color = palette.onBackground.copy(alpha = 0.12f))

                AnimatedContent(
                    targetState = moduleId to page,
                    transitionSpec = {
                        (fadeIn(tween(320)) + slideInHorizontally { it / 4 }) togetherWith
                            (fadeOut(tween(220)) + slideOutHorizontally { -it / 6 })
                    },
                    label = "lesson-page",
                    modifier = Modifier.weight(1f),
                ) { (_, currentPage) ->
                    Column(
                        Modifier
                            .fillMaxSize()
                            .verticalScroll(scrollState)
                            .padding(horizontal = 16.dp, vertical = 12.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp),
                    ) {
                        when (currentPage) {
                            LessonPage.Theory -> TheoryPage(
                                markdown = theoryMarkdown,
                                glossary = glossary,
                                palette = palette,
                                fontScale = readerSettings.fontScale,
                                onCopy = {
                                    copyToClipboard(theoryMarkdown)
                                    viewModel.showMessage("Текст урока скопирован")
                                },
                                onContinue = { viewModel.completeTheory() },
                                note = note,
                                bookmarked = bookmarked,
                                onNoteChange = viewModel::updateNote,
                                onSaveNote = viewModel::saveNote,
                                onToggleBookmark = viewModel::toggleBookmark,
                            )
                            LessonPage.Practice -> PracticePage(
                                prompt = practicePrompt,
                                onPromptChange = viewModel::updatePracticePrompt,
                                generated = generatedText,
                                aiStatus = aiStatus,
                                onGenerate = viewModel::generateFromPrompt,
                                palette = palette,
                                fontScale = readerSettings.fontScale,
                                module = current,
                                sandboxResult = sandboxResult,
                                challengeFeedback = challengeFeedback,
                                onRunSandbox = viewModel::runSandbox,
                                onEvaluateChallenge = viewModel::evaluateChallenge,
                                onComplete = { viewModel.completePractice() },
                                onCopyPrompt = {
                                    copyToClipboard(practicePrompt)
                                    viewModel.showMessage("Промт скопирован")
                                },
                            )
                            LessonPage.Quiz -> QuizPage(
                                module = current,
                                onComplete = {
                                    viewModel.completeQuiz()
                                    viewModel.showMessage("Тест пройден")
                                },
                                onSkip = viewModel::skipQuiz,
                                nextModuleId = nextModuleId,
                                onNext = { id ->
                                    viewModel.openLesson(id)
                                    onNextModule?.invoke(id)
                                },
                                onFinish = onBack,
                                palette = palette,
                            )
                        }
                    }
                }
            }
        }

        if (drawerOpen) {
            Box(
                Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.35f))
                    .clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                    ) { drawerOpen = false },
            )
        }

        LessonDrawer(
            items = lessonItems,
            offsetX = drawerOffset,
            palette = palette,
            onSelect = { id ->
                drawerOpen = false
                viewModel.openLesson(id)
                onNextModule?.invoke(id)
            },
            onClose = { drawerOpen = false },
        )
    }
}

@Composable
private fun LessonTopBar(
    onBack: () -> Unit,
    onMenu: () -> Unit,
    page: LessonPage,
    onPageSelect: (LessonPage) -> Unit,
    settingsExpanded: Boolean,
    onToggleSettings: () -> Unit,
) {
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(onClick = onMenu) { Text("☰") }
        IconButton(onClick = onBack) { Text("←") }
        Row(Modifier.weight(1f), horizontalArrangement = Arrangement.Center) {
            LessonPage.entries.forEach { p ->
                val selected = p == page
                FilterChip(
                    selected = selected,
                    onClick = { onPageSelect(p) },
                    label = {
                        Text(
                            when (p) {
                                LessonPage.Theory -> "Теория"
                                LessonPage.Practice -> "Практика"
                                LessonPage.Quiz -> "Тест"
                            },
                        )
                    },
                    modifier = Modifier.padding(horizontal = 2.dp),
                )
            }
        }
        IconButton(onClick = onToggleSettings) {
            Text(if (settingsExpanded) "Aa▾" else "Aa")
        }
    }
}

@Composable
private fun LessonHeader(
    title: String,
    chapter: String?,
    summary: String?,
    lessonIndex: Int,
    totalLessons: Int,
    durationMinutes: Int?,
    progress: Float,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
) {
    Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp)) {
        Text(title, style = MaterialTheme.typography.headlineSmall, color = palette.onBackground)
        chapter?.let {
            Text("Раздел: $it", style = MaterialTheme.typography.labelLarge, color = palette.accent)
        }
        summary?.let {
            Text(it, style = MaterialTheme.typography.bodyMedium, color = palette.onSurface.copy(alpha = 0.85f))
        }
        Text(
            "Урок $lessonIndex из $totalLessons" + (durationMinutes?.let { " · ~$it мин" } ?: ""),
            style = MaterialTheme.typography.bodySmall,
            color = palette.onSurface.copy(alpha = 0.7f),
        )
        LinearProgressIndicator(
            progress = { progress },
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
            color = palette.accent,
        )
    }
}

@Composable
private fun ReaderSettingsPanel(
    fontScale: Float,
    temperature: Double,
    tone: ReaderColorTone,
    onFontScale: (Float) -> Unit,
    onTemperature: (Double) -> Unit,
    onTone: (ReaderColorTone) -> Unit,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
) {
    Card(
        Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = palette.surface),
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Окно чтения", style = MaterialTheme.typography.titleSmall, color = palette.onSurface)
            Text("Размер шрифта", style = MaterialTheme.typography.labelMedium, color = palette.onSurface)
            Slider(
                value = fontScale,
                onValueChange = onFontScale,
                valueRange = 0.85f..1.45f,
            )
            Text("Температура ИИ: ${"%.1f".format(temperature)}", color = palette.onSurface)
            Slider(
                value = temperature.toFloat(),
                onValueChange = { onTemperature(it.toDouble()) },
                valueRange = 0f..1.5f,
            )
            Text("Тон экрана", style = MaterialTheme.typography.labelMedium, color = palette.onSurface)
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                ReaderColorTone.entries.forEach { t ->
                    FilterChip(
                        selected = tone == t,
                        onClick = { onTone(t) },
                        label = {
                            Text(
                                when (t) {
                                    ReaderColorTone.Day -> "День"
                                    ReaderColorTone.Night -> "Ночь"
                                    ReaderColorTone.Warm -> "Тёплый"
                                    ReaderColorTone.Cool -> "Холодный"
                                },
                            )
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun TheoryPage(
    markdown: String,
    note: String,
    bookmarked: Boolean,
    onNoteChange: (String) -> Unit,
    onSaveNote: () -> Unit,
    onToggleBookmark: () -> Unit,
    glossary: List<com.neuropoligon.domain.content.GlossaryEntry>,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
    fontScale: Float,
    onCopy: () -> Unit,
    onContinue: () -> Unit,
) {
    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = palette.surface),
    ) {
        Column(Modifier.padding(18.dp)) {
            Text("Теория", style = MaterialTheme.typography.titleLarge, color = palette.accent)
            Spacer(Modifier.height(12.dp))
            if (markdown.isBlank()) {
                Text("Загрузка…", color = palette.onSurface)
            } else {
                LessonRichMarkdown(
                    markdown = markdown,
                    entries = glossary,
                    palette = palette,
                    fontScale = fontScale,
                )
            }
        }
    }
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = palette.surface)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Text("Моя заметка", style = MaterialTheme.typography.titleMedium, color = palette.onSurface); TextButton(onClick = onToggleBookmark) { Text(if (bookmarked) "★ В закладках" else "☆ В закладки") } }
            OutlinedTextField(value = note, onValueChange = onNoteChange, modifier = Modifier.fillMaxWidth(), minLines = 3, placeholder = { Text("Запишите вывод или пример применения") })
            OutlinedButton(onClick = onSaveNote, modifier = Modifier.fillMaxWidth()) { Text("Сохранить заметку") }
        }
    }
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        OutlinedButton(onClick = onCopy, modifier = Modifier.weight(1f)) { Text("Копировать") }
        Button(onClick = onContinue, modifier = Modifier.weight(1f)) { Text("К практике →") }
    }
}

@Composable
private fun PracticePage(
    prompt: String,
    onPromptChange: (String) -> Unit,
    generated: String,
    aiStatus: AiConnectionStatus,
    onGenerate: () -> Unit,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
    fontScale: Float,
    module: com.neuropoligon.domain.content.Module,
    sandboxResult: com.neuropoligon.domain.sandbox.SandboxResult?,
    challengeFeedback: String?,
    onRunSandbox: (SandboxType, SandboxConfig, SandboxUserInput) -> Unit,
    onEvaluateChallenge: (com.neuropoligon.domain.content.Challenge, Map<String, Double>) -> Unit,
    onComplete: () -> Unit,
    onCopyPrompt: () -> Unit,
) {
    Card(
        Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = palette.promptContainer.copy(alpha = 0.35f)),
    ) {
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Практика", style = MaterialTheme.typography.titleLarge, color = palette.promptOn)
            Text(
                "Промт выполняется здесь через ваш API-ключ. Настройте температуру в панели «Aa».",
                style = MaterialTheme.typography.bodyMedium,
                color = palette.onSurface,
            )
            OutlinedTextField(
                value = prompt,
                onValueChange = onPromptChange,
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Промт") },
                minLines = 10,
            )
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Button(
                    onClick = onGenerate,
                    enabled = aiStatus != AiConnectionStatus.Generating,
                    modifier = Modifier.weight(1f),
                ) {
                    if (aiStatus == AiConnectionStatus.Generating) {
                        CircularProgressIndicator(Modifier.size(18.dp), strokeWidth = 2.dp)
                        Spacer(Modifier.width(8.dp))
                    }
                    Text(if (aiStatus == AiConnectionStatus.Generating) "Генерация…" else "Сгенерировать")
                }
                AiConnectionIndicator(status = aiStatus)
            }
            OutlinedButton(onClick = onCopyPrompt, modifier = Modifier.fillMaxWidth()) {
                Text("Скопировать промт")
            }
            if (generated.isNotBlank()) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = palette.surface),
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(
                        generated,
                        modifier = Modifier.padding(14.dp),
                        color = palette.onSurface,
                        fontSize = (15f * fontScale).sp,
                    )
                }
            }
        }
    }

    module.blocks.filterIsInstance<Block.Sandbox>().forEach { block ->
        var input by remember(block.sandboxType, module.id) { mutableStateOf(block.config.prompt) }
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Демо: ${block.sandboxType}", style = MaterialTheme.typography.titleMedium)
                OutlinedTextField(
                    value = input,
                    onValueChange = { input = it },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 2,
                )
                Button(
                    onClick = {
                        onRunSandbox(block.sandboxType, block.config, SandboxUserInput(text = input))
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Запустить демо") }
                sandboxResult?.let { SandboxResultView(it) }
            }
        }
    }

    module.blocks.filterIsInstance<Block.ChallengeBlock>().forEach { block ->
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(14.dp)) {
                Text(block.challenge.title, style = MaterialTheme.typography.titleMedium)
                Text(block.challenge.description)
                Button(
                    onClick = {
                        val params = when (val c = block.challenge.criterion) {
                            is ChallengeCriterion.SandboxParam ->
                                mapOf(c.paramName to c.value)
                            else -> emptyMap()
                        }
                        onEvaluateChallenge(block.challenge, params)
                    },
                    modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
                ) { Text("Проверить") }
                challengeFeedback?.let { Text(it, modifier = Modifier.padding(top = 6.dp)) }
            }
        }
    }

    Button(onClick = onComplete, modifier = Modifier.fillMaxWidth()) {
        Text("Практику выполнил → к тесту")
    }
}

@Composable
private fun QuizPage(
    module: com.neuropoligon.domain.content.Module,
    onComplete: () -> Unit,
    onSkip: () -> Unit,
    nextModuleId: String?,
    onNext: (String) -> Unit,
    onFinish: () -> Unit,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
) {
    val quiz = module.blocks.filterIsInstance<Block.Quiz>().firstOrNull()
    Card(
        Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = palette.surface),
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("Мини-тест", style = MaterialTheme.typography.titleLarge, color = palette.accent)
            if (quiz == null) {
                Text("Для этого урока тест не задан.", color = palette.onSurface)
            } else {
                QuizBlockView(quiz, onCompleted = onComplete)
            }
        }
    }
    TextButton(onClick = onSkip, modifier = Modifier.fillMaxWidth()) {
        Text("Пропустить тест")
    }
    if (nextModuleId != null) {
        Button(
            onClick = { onNext(nextModuleId) },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Следующий урок →") }
    } else {
        OutlinedButton(onClick = onFinish, modifier = Modifier.fillMaxWidth()) {
            Text("На главный экран")
        }
    }
}

@Composable
private fun AiConnectionIndicator(status: AiConnectionStatus) {
    val (color, label) = when (status) {
        AiConnectionStatus.Ready -> Color(0xFF16A34A) to "Онлайн"
        AiConnectionStatus.NoApiKey -> Color(0xFFF59E0B) to "Нет ключа"
        AiConnectionStatus.Generating -> Color(0xFF3B82F6) to "…"
        AiConnectionStatus.Error -> Color(0xFFDC2626) to "Ошибка"
        AiConnectionStatus.Unknown -> Color(0xFF94A3B8) to "?"
    }
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier
                .size(14.dp)
                .clip(CircleShape)
                .background(color),
        )
        Text(label, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun LessonDrawer(
    items: List<LessonListItem>,
    offsetX: androidx.compose.ui.unit.Dp,
    palette: com.neuropoligon.presentation.lesson.LessonReaderPalette,
    onSelect: (String) -> Unit,
    onClose: () -> Unit,
) {
    Card(
        Modifier
            .width(drawerWidth)
            .fillMaxHeight()
            .offset(x = offsetX)
            .padding(vertical = 0.dp),
        shape = RoundedCornerShape(topEnd = 20.dp, bottomEnd = 20.dp),
        colors = CardDefaults.cardColors(containerColor = palette.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
    ) {
        Column(Modifier.fillMaxSize().padding(12.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Все уроки", style = MaterialTheme.typography.titleMedium, color = palette.onSurface)
                IconButton(onClick = onClose) { Text("✕") }
            }
            Column(
                Modifier
                    .weight(1f)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items.forEach { item ->
                    val bg = if (item.isCurrent) palette.accent.copy(alpha = 0.15f) else Color.Transparent
                    Column(
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(10.dp))
                            .background(bg)
                            .clickable { onSelect(item.moduleId) }
                            .padding(10.dp),
                    ) {
                        item.chapterTitle?.let {
                            Text(it, style = MaterialTheme.typography.labelSmall, color = palette.accent)
                        }
                        Text(
                            item.title,
                            style = MaterialTheme.typography.bodyMedium,
                            color = if (item.isCurrent) palette.accent else palette.onSurface,
                        )
                    }
                }
            }
        }
    }
}
