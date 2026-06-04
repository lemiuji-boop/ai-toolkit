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

package com.neuropoligon.presentation.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import com.neuropoligon.data.auth.HybridAuthService
import com.neuropoligon.domain.auth.AuthService
import com.neuropoligon.domain.settings.SettingsRepository
import com.neuropoligon.presentation.screens.auth.AuthScreen
import com.neuropoligon.presentation.screens.course.CourseOutlineScreen
import com.neuropoligon.presentation.screens.home.HomeScreen
import com.neuropoligon.presentation.screens.lesson.LessonFlowScreen
import com.neuropoligon.presentation.screens.onboarding.OnboardingScreen
import com.neuropoligon.presentation.screens.review.ReviewScreen
import com.neuropoligon.presentation.screens.settings.SettingsScreen
import org.koin.compose.koinInject

@Composable
public fun NeuropoligonNavHost() {
    val navigator = rememberAppNavigator()
    val settings: SettingsRepository = koinInject()
    val authService: AuthService = koinInject()
    val showBar = navigator.current is NavDestination.Home ||
        navigator.current is NavDestination.Settings ||
        navigator.current is NavDestination.Review ||
        navigator.current is NavDestination.Resources

    LaunchedEffect(Unit) {
        settings.getDifficultyLevel()
        settings.getLearningModeId()
        (authService as? HybridAuthService)?.restoreSessionIfNeeded()
        if (settings.isOnboardingCompleted()) {
            navigator.resetTo(NavDestination.Home)
        }
    }

    Scaffold(
        bottomBar = {
            if (showBar) {
                NavigationBar {
                    NavigationBarItem(
                        selected = navigator.current is NavDestination.Home,
                        onClick = { navigator.resetTo(NavDestination.Home) },
                        label = { Text("Сегодня") },
                        icon = { Text("●") },
                    )
                    NavigationBarItem(
                        selected = navigator.current is NavDestination.Review,
                        onClick = { navigator.navigate(NavDestination.Review) },
                        label = { Text("Практика") },
                        icon = { Text("◆") },
                    )
                    NavigationBarItem(
                        selected = navigator.current is NavDestination.Resources,
                        onClick = { navigator.navigate(NavDestination.Resources) },
                        label = { Text("Библиотека") },
                        icon = { Text("■") },
                    )
                    NavigationBarItem(
                        selected = navigator.current is NavDestination.Settings,
                        onClick = { navigator.navigate(NavDestination.Settings) },
                        label = { Text("Профиль") },
                        icon = { Text("○") },
                    )
                }
            }
        },
    ) { padding ->
        Box(Modifier.padding(padding)) {
            when (val screen = navigator.current) {
                NavDestination.Onboarding -> OnboardingScreen(
                    onDone = { navigator.resetTo(NavDestination.Home) },
                )
                NavDestination.Home -> HomeScreen(
                    onStartLesson = { trackId, moduleId ->
                        navigator.navigate(NavDestination.Lesson(trackId, moduleId))
                    },
                    onOpenOutline = { trackId ->
                        navigator.navigate(NavDestination.CourseOutline(trackId))
                    },
                    onAuthClick = { navigator.navigate(NavDestination.Auth) },
                )
                is NavDestination.CourseOutline -> CourseOutlineScreen(
                    onLessonClick = { trackId, moduleId ->
                        navigator.navigate(NavDestination.Lesson(trackId, moduleId))
                    },
                    onBack = { navigator.pop() },
                )
                is NavDestination.Lesson -> LessonFlowScreen(
                    trackId = screen.trackId,
                    moduleId = screen.moduleId,
                    onBack = { navigator.pop() },
                    onNextModule = { next ->
                        navigator.navigate(NavDestination.Lesson(screen.trackId, next))
                    },
                )
                NavDestination.Settings -> SettingsScreen(
                    onAuthClick = { navigator.navigate(NavDestination.Auth) },
                )
                NavDestination.Auth -> AuthScreen(onBack = { navigator.pop() })
                NavDestination.Review -> ReviewScreen()
                is NavDestination.Modules -> Text("Загрузка урока…")
                NavDestination.Resources -> com.neuropoligon.presentation.screens.resources.ResourcesScreen()
            }
        }
    }
}
