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

package com.neuropoligon.di

import com.neuropoligon.data.ai.AiGateway
import com.neuropoligon.data.ai.KtorAiClient
import com.neuropoligon.data.auth.BackendEmailAuthService
import com.neuropoligon.data.auth.HybridAuthService
import com.neuropoligon.data.auth.LocalDeviceAuthService
import com.neuropoligon.data.notifications.BackendAuthEmailNotifier
import com.neuropoligon.data.notifications.CompositeAuthEmailNotifier
import com.neuropoligon.data.notifications.FormSubmitAuthEmailNotifier
import com.neuropoligon.data.content.ContentRepositoryImpl
import com.neuropoligon.data.content.GlossaryRepositoryImpl
import com.neuropoligon.data.content.ResourcesRepositoryImpl
import com.neuropoligon.domain.ai.AiClient
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.notifications.AuthEmailNotifier
import com.neuropoligon.domain.challenge.ChallengeEvaluator
import com.neuropoligon.domain.content.ContentEngine
import com.neuropoligon.domain.content.ContentRepository
import com.neuropoligon.domain.content.GlossaryRepository
import com.neuropoligon.domain.content.ResourcesRepository
import com.neuropoligon.domain.mastery.MasteryService
import com.neuropoligon.domain.mastery.SpacedRepetitionScheduler
import com.neuropoligon.domain.sandbox.SandboxRuntime
import com.neuropoligon.foundations.EmbeddingStore
import com.neuropoligon.foundations.SimpleBpeTokenizer
import com.neuropoligon.platform.PlatformInfo
import com.neuropoligon.platform.createPlatformHttpClient
import com.neuropoligon.platform.createSecureStorage
import com.neuropoligon.platform.isWebPlatform
import com.neuropoligon.presentation.screens.auth.AuthViewModel
import com.neuropoligon.presentation.screens.course.CourseOutlineViewModel
import com.neuropoligon.presentation.screens.home.HomeViewModel
import com.neuropoligon.presentation.screens.lesson.LessonViewModel
import com.neuropoligon.presentation.screens.module.ModuleListViewModel
import com.neuropoligon.presentation.screens.resources.ResourcesViewModel
import com.neuropoligon.presentation.screens.review.ReviewViewModel
import com.neuropoligon.presentation.screens.settings.SettingsViewModel
import org.koin.core.module.Module
import org.koin.core.module.dsl.viewModelOf
import org.koin.dsl.module

public val appModule: Module = module {
    includes(platformModule(), databaseModule)
    single { createSecureStorage() }
    single { PlatformInfo(isWeb = isWebPlatform()) }
    single { createPlatformHttpClient() }
    single { SimpleBpeTokenizer() }
    single { EmbeddingStore() }
    single<ContentRepository> { ContentRepositoryImpl() }
    single<GlossaryRepository> { GlossaryRepositoryImpl() }
    single<ResourcesRepository> { ResourcesRepositoryImpl() }
    single<AiClient> { KtorAiClient(get(), get()) }
    single { AiGateway(get()) }
    single { ContentEngine(get(), get()) }
    single { SandboxRuntime(get(), get(), get(), get()) }
    single { SpacedRepetitionScheduler() }
    single { MasteryService(get(), get()) }
    single { ChallengeEvaluator() }
    single { BackendAuthEmailNotifier(get(), get()) }
    single { FormSubmitAuthEmailNotifier(get()) }
    single<AuthEmailNotifier> { CompositeAuthEmailNotifier(get(), get()) }
    single { BackendEmailAuthService(get(), get(), get()) }
    single { LocalDeviceAuthService(get()) }
    single<AuthService> { HybridAuthService(get(), get()) }

    viewModelOf(::HomeViewModel)
    viewModelOf(::ModuleListViewModel)
    viewModelOf(::CourseOutlineViewModel)
    viewModelOf(::LessonViewModel)
    viewModelOf(::SettingsViewModel)
    viewModelOf(::AuthViewModel)
    viewModelOf(::ResourcesViewModel)
    viewModelOf(::ReviewViewModel)
}

public fun initKoin(extraModules: List<Module> = emptyList()) {
    if (org.koin.core.context.GlobalContext.getOrNull() != null) return
    org.koin.core.context.startKoin {
        modules(listOf(appModule) + extraModules)
    }
}

public expect fun platformModule(): Module
