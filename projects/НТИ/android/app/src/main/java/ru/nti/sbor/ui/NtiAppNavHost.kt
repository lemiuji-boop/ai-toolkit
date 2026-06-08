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

package ru.nti.sbor.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import kotlinx.coroutines.launch
import ru.nti.sbor.AppContainer
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.auth.LoginScreen
import ru.nti.sbor.ui.auth.LoginViewModel
import ru.nti.sbor.ui.auth.LoginViewModelFactory
import ru.nti.sbor.ui.design.AppDesignVariant
import ru.nti.sbor.ui.design.LocalAppDesignVariant
import ru.nti.sbor.ui.home.HomeScreen
import ru.nti.sbor.ui.home.HomeViewModel
import ru.nti.sbor.ui.home.HomeViewModelFactory
import ru.nti.sbor.ui.navigation.Routes
import ru.nti.sbor.ui.record.RecordFormScreen
import ru.nti.sbor.ui.record.RecordFormViewModel
import ru.nti.sbor.ui.record.RecordFormViewModelFactory
import ru.nti.sbor.ui.settings.SettingsScreen
import ru.nti.sbor.ui.settings.SettingsViewModel
import ru.nti.sbor.ui.settings.SettingsViewModelFactory
import ru.nti.sbor.ui.shell.NtiAppShell
import ru.nti.sbor.ui.theme.NtiAccessibilityProvider
import ru.nti.sbor.ui.theme.NtiSborTheme

@Composable
fun NtiAppNavHost(
    container: AppContainer,
    designVariant: AppDesignVariant,
    initialTheme: ThemeMode,
) {
    CompositionLocalProvider(LocalAppDesignVariant provides designVariant) {
        val accessibility by container.appPreferences.accessibility.collectAsState(
            initial = ru.nti.sbor.data.settings.AccessibilityPrefs(themeMode = initialTheme),
        )
        val loggedIn by container.authRepository.loggedIn.collectAsState()

        NtiSborTheme(themeMode = accessibility.themeMode) {
            NtiAccessibilityProvider(accessibility) {
                val navController = rememberNavController()
                val accountName = container.secureServerSettings.getDisplayName()
                val useDrawer = designVariant.usesV2Chrome() && loggedIn

                LaunchedEffect(loggedIn) {
                    val dest = navController.currentDestination?.route
                    if (!loggedIn && dest != Routes.LOGIN) {
                        navController.navigate(Routes.LOGIN) {
                            popUpTo(0) { inclusive = true }
                            launchSingleTop = true
                        }
                    }
                }

                val scope = rememberCoroutineScope()
                val navigateLogout: () -> Unit = {
                    scope.launch {
                        container.authRepository.logout()
                        navController.navigate(Routes.LOGIN) {
                            popUpTo(0) { inclusive = true }
                            launchSingleTop = true
                        }
                    }
                }

                LaunchedEffect(Unit) {
                    if (loggedIn) {
                        container.authRepository.validateSession()
                    }
                }

                if (useDrawer) {
                    NtiAppShell(
                        navController = navController,
                        accountName = accountName,
                        drawerEnabled = true,
                        onLogout = navigateLogout,
                    ) { onOpenMenu ->
                        AppNavHostContent(
                            container = container,
                            designVariant = designVariant,
                            navController = navController,
                            startDestination = if (loggedIn) Routes.HOME else Routes.LOGIN,
                            onOpenMenu = onOpenMenu,
                        )
                    }
                } else {
                    AppNavHostContent(
                        container = container,
                        designVariant = designVariant,
                        navController = navController,
                        startDestination = if (loggedIn) Routes.HOME else Routes.LOGIN,
                        onOpenMenu = {},
                    )
                }
            }
        }
    }
}

@Composable
private fun AppNavHostContent(
    container: AppContainer,
    designVariant: AppDesignVariant,
    navController: androidx.navigation.NavHostController,
    startDestination: String,
    onOpenMenu: () -> Unit,
) {
    NavHost(navController = navController, startDestination = startDestination) {
        composable(Routes.LOGIN) {
            val vm: LoginViewModel = viewModel(factory = LoginViewModelFactory(container))
            LoginScreen(
                viewModel = vm,
                onLoggedIn = {
                    container.authRepository.refreshAuthState()
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                        launchSingleTop = true
                    }
                },
            )
        }
        composable(Routes.HOME) {
            val vm: HomeViewModel = viewModel(factory = HomeViewModelFactory(container))
            HomeScreen(
                viewModel = vm,
                designVariant = designVariant,
                onAdd = { navController.navigate(Routes.RECORD_NEW) },
                onEdit = { id -> navController.navigate(Routes.recordEdit(id)) },
                onSettings = { navController.navigate(Routes.SETTINGS) },
                onOpenMenu = onOpenMenu,
            )
        }
        composable(Routes.RECORD_NEW) {
            val vm: RecordFormViewModel = viewModel(
                factory = RecordFormViewModelFactory(container, null),
            )
            RecordFormScreen(
                viewModel = vm,
                designVariant = designVariant,
                onBack = { navController.popBackStack() },
            )
        }
        composable(
            route = Routes.RECORD_EDIT,
            arguments = listOf(navArgument("id") { type = NavType.LongType }),
        ) { entry ->
            val id = entry.arguments?.getLong("id") ?: 0L
            val vm: RecordFormViewModel = viewModel(
                factory = RecordFormViewModelFactory(container, id),
            )
            RecordFormScreen(
                viewModel = vm,
                designVariant = designVariant,
                onBack = { navController.popBackStack() },
            )
        }
        composable(Routes.SETTINGS) {
            val vm: SettingsViewModel = viewModel(factory = SettingsViewModelFactory(container))
            SettingsScreen(
                viewModel = vm,
                designVariant = designVariant,
                onBack = { navController.popBackStack() },
            )
        }
    }
}
