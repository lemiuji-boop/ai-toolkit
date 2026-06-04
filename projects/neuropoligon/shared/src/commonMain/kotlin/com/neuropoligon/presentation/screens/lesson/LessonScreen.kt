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

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.relocation.BringIntoViewRequester
import androidx.compose.foundation.relocation.bringIntoViewRequester
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.Block
import com.neuropoligon.domain.content.ChallengeCriterion
import com.neuropoligon.domain.sandbox.SandboxUserInput
import com.neuropoligon.platform.copyToClipboard
import com.neuropoligon.presentation.glossary.GlossaryMarkdown
import com.neuropoligon.presentation.lesson.LessonStepCard
import com.neuropoligon.presentation.lesson.PracticeBlockView
import com.neuropoligon.presentation.lesson.QuizBlockView
import com.neuropoligon.presentation.sandbox.SandboxResultView
import kotlinx.coroutines.launch
import org.koin.compose.viewmodel.koinViewModel

@OptIn(ExperimentalFoundationApi::class)
@Composable
public fun LessonScreen(
    trackId: String,
    moduleId: String,
    onBack: () -> Unit,
    onNextModule: ((String) -> Unit)? = null,
    viewModel: LessonViewModel = koinViewModel(),
) {
    LaunchedEffect(trackId, moduleId) { viewModel.load(trackId, moduleId) }
    val module by viewModel.module.collectAsState()
    val glossary by viewModel.glossary.collectAsState()
    val sandboxResult by viewModel.sandboxResult.collectAsState()
    val challengeFeedback by viewModel.challengeFeedback.collectAsState()
    val progress by viewModel.courseProgress.collectAsState()
    val lessonIndex by viewModel.lessonIndex.collectAsState()
    val totalLessons by viewModel.totalLessons.collectAsState()
    val nextModuleId by viewModel.nextModuleId.collectAsState()
    val uiMessage by viewModel.uiMessage.collectAsState()
    val sandboxInputs = remember(moduleId) { mutableStateMapOf<Int, String>() }
    val snackbarHostState = remember { SnackbarHostState() }
    val scrollState = rememberScrollState()
    val scope = rememberCoroutineScope()
    val practiceRequester = remember { BringIntoViewRequester() }
    val demoRequester = remember { BringIntoViewRequester() }
    val pulse = rememberInfiniteTransition(label = "next-pulse")
    val nextScale by pulse.animateFloat(
        initialValue = 1f,
        targetValue = 1.03f,
        animationSpec = infiniteRepeatable(animation = tween(900), repeatMode = RepeatMode.Reverse),
        label = "next-scale",
    )

    LaunchedEffect(uiMessage) {
        uiMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearMessage()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MaterialTheme.colorScheme.background,
    ) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
        ) {
            IconButton(onClick = onBack) {
                Text("←", color = MaterialTheme.colorScheme.onBackground)
            }
            if (module == null) {
                Column(
                    Modifier.fillMaxSize(),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    CircularProgressIndicator()
                    Text(
                        "Загрузка урока…",
                        modifier = Modifier.padding(top = 12.dp),
                        color = MaterialTheme.colorScheme.onBackground,
                    )
                }
                return@Column
            }

            val current = module!!
            Text(current.title, style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.onBackground)
            current.chapterTitle?.let { chapter ->
                Text("Раздел: $chapter", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
            current.summary?.let {
                Text(it, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Text(
                "Урок $lessonIndex из $totalLessons" +
                    (current.durationMinutes?.let { " · ~$it мин" } ?: ""),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            )

            Column(
                Modifier.weight(1f).verticalScroll(scrollState),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                val blocks = current.blocks
                blocks.forEachIndexed { index, block ->
                    val stepLabel = "Шаг ${index + 1} из ${blocks.size}"
                    when (block) {
                        is Block.Explanation -> {
                            val md by produceState(initialValue = "", block, moduleId) {
                                value = viewModel.markdownFor(block)
                            }
                            LessonStepCard(stepLabel = stepLabel, sectionTitle = "Теория") {
                                if (md.isBlank()) {
                                    Text("Текст урока загружается…", color = MaterialTheme.colorScheme.onSurfaceVariant)
                                } else {
                                    GlossaryMarkdown(md, glossary)
                                }
                                TextButton(onClick = {
                                    copyToClipboard(md)
                                    viewModel.showMessage("Текст урока скопирован")
                                }) { Text("Скопировать текст урока") }
                                OutlinedButton(
                                    onClick = {
                                        scope.launch {
                                            practiceRequester.bringIntoView()
                                        }
                                    },
                                    modifier = Modifier.fillMaxWidth(),
                                ) { Text("Перейти к практике ↓") }
                                Button(
                                    onClick = { viewModel.completeBlock("exp-$moduleId-$index") },
                                    modifier = Modifier.fillMaxWidth(),
                                ) { Text("Понял, отметить теорию") }
                            }
                        }
                        is Block.Practice -> {
                            LessonStepCard(
                                stepLabel = stepLabel,
                                sectionTitle = "Практика: ${block.title}",
                                modifier = Modifier.bringIntoViewRequester(practiceRequester),
                            ) {
                                PracticeBlockView(block) { viewModel.showMessage(it) }
                                Button(
                                    onClick = { viewModel.completeBlock("practice-$moduleId") },
                                    modifier = Modifier.fillMaxWidth(),
                                ) { Text("Практику выполнил") }
                            }
                        }
                        is Block.Quiz -> {
                            LessonStepCard(stepLabel = stepLabel, sectionTitle = "Мини-тест") {
                                QuizBlockView(block) {
                                    viewModel.completeBlock("quiz-$moduleId")
                                    viewModel.showMessage("Мини-тест пройден")
                                }
                            }
                        }
                        is Block.Sandbox -> {
                            val input = sandboxInputs.getOrPut(index) { block.config.prompt }
                            var running by remember(block, moduleId) { mutableStateOf(false) }
                            LessonStepCard(
                                stepLabel = stepLabel,
                                sectionTitle = "Интерактивная демо",
                                modifier = Modifier.bringIntoViewRequester(demoRequester),
                            ) {
                                OutlinedTextField(
                                    value = input,
                                    onValueChange = { sandboxInputs[index] = it },
                                    label = { Text("Ваш запрос / текст") },
                                    modifier = Modifier.fillMaxWidth(),
                                    minLines = 2,
                                )
                                Button(
                                    onClick = {
                                        running = true
                                        viewModel.runSandbox(
                                            block.sandboxType,
                                            block.config,
                                            SandboxUserInput(text = input),
                                        )
                                        running = false
                                        viewModel.showMessage("Демо обновлено")
                                    },
                                    enabled = !running,
                                    modifier = Modifier.fillMaxWidth(),
                                ) { Text(if (running) "Запуск…" else "Запустить демо") }
                                sandboxResult?.let { SandboxResultView(it) }
                            }
                        }
                        is Block.ChallengeBlock -> {
                            LessonStepCard(stepLabel = stepLabel, sectionTitle = block.challenge.title) {
                                Text(block.challenge.description, color = MaterialTheme.colorScheme.onSurface)
                                Button(
                                    onClick = {
                                        val inp = sandboxInputs.values.firstOrNull().orEmpty()
                                        val params = when (val c = block.challenge.criterion) {
                                            is ChallengeCriterion.SandboxParam ->
                                                mapOf(c.paramName to (inp.toDoubleOrNull() ?: c.value))
                                            else -> emptyMap()
                                        }
                                        viewModel.evaluateChallenge(block.challenge, params)
                                    },
                                    modifier = Modifier.fillMaxWidth(),
                                ) { Text("Проверить себя") }
                                AnimatedVisibility(visible = challengeFeedback != null) {
                                    challengeFeedback?.let { Text(it, color = MaterialTheme.colorScheme.onSurface) }
                                }
                            }
                        }
                        is Block.CodeRecipe -> {
                            LessonStepCard(stepLabel = stepLabel, sectionTitle = "Шпаргалка (${block.language})") {
                                Text(block.note, color = MaterialTheme.colorScheme.onSurface)
                                Text(block.code, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurface)
                                Button(onClick = {
                                    copyToClipboard(block.code)
                                    viewModel.showMessage("Код скопирован")
                                }) { Text("Скопировать код") }
                            }
                        }
                    }
                }

                AnimatedVisibility(visible = nextModuleId != null) {
                    Button(
                        onClick = { nextModuleId?.let { id -> onNextModule?.invoke(id) } },
                        modifier = Modifier.fillMaxWidth().scale(nextScale),
                    ) { Text("Следующий урок →") }
                }
                AnimatedVisibility(visible = nextModuleId == null) {
                    OutlinedButton(onClick = onBack, modifier = Modifier.fillMaxWidth()) {
                        Text("На главный экран")
                    }
                }
            }
        }
    }
}
