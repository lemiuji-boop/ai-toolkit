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

package ru.nti.sbor.ui.shell

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.NavigationDrawerItem
import androidx.compose.material3.NavigationDrawerItemDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavHostController
import kotlinx.coroutines.launch
import ru.nti.sbor.ui.design.NtiV2BrandTitle
import ru.nti.sbor.ui.design.NtiV2Design
import ru.nti.sbor.ui.navigation.Routes
import ru.nti.sbor.ui.theme.NtiTokens

/** Боковое меню: главная, настройки, выход. */
@Composable
fun NtiAppShell(
    navController: NavHostController,
    accountName: String,
    drawerEnabled: Boolean,
    onLogout: () -> Unit,
    content: @Composable (onOpenMenu: () -> Unit) -> Unit,
) {
    val drawerState = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val openMenu: () -> Unit = {
        if (drawerEnabled) {
            scope.launch { drawerState.open() }
        }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = drawerEnabled,
        drawerContent = {
            if (!drawerEnabled) return@ModalNavigationDrawer
            ModalDrawerSheet(drawerContainerColor = NtiV2Design.CardBg) {
                Column(Modifier.padding(NtiTokens.SpacingMd)) {
                    NtiV2BrandTitle()
                    if (accountName.isNotBlank()) {
                        Text(
                            accountName,
                            color = NtiV2Design.TextMuted,
                            style = MaterialTheme.typography.bodySmall,
                            modifier = Modifier.padding(top = NtiTokens.SpacingXs),
                        )
                    }
                }
                DrawerEntry(
                    label = "Главная",
                    icon = Icons.Default.Home,
                    selected = navController.currentDestination?.route == Routes.HOME,
                    onClick = {
                        scope.launch { drawerState.close() }
                        navController.navigate(Routes.HOME) {
                            popUpTo(Routes.HOME) { inclusive = true }
                            launchSingleTop = true
                        }
                    },
                )
                DrawerEntry(
                    label = "Оформление",
                    icon = Icons.Default.Settings,
                    selected = navController.currentDestination?.route == Routes.SETTINGS,
                    onClick = {
                        scope.launch { drawerState.close() }
                        navController.navigate(Routes.SETTINGS)
                    },
                )
                DrawerEntry(
                    label = "Выйти",
                    icon = Icons.AutoMirrored.Filled.ExitToApp,
                    selected = false,
                    onClick = {
                        scope.launch { drawerState.close() }
                        onLogout()
                    },
                )
            }
        },
    ) {
        content(openMenu)
    }
}

@Composable
private fun DrawerEntry(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    onClick: () -> Unit,
) {
    NavigationDrawerItem(
        label = { Text(label, color = NtiV2Design.TextPrimary) },
        selected = selected,
        onClick = onClick,
        icon = { Icon(icon, contentDescription = label, tint = NtiV2Design.AccentBlue) },
        colors = NavigationDrawerItemDefaults.colors(
            selectedContainerColor = NtiV2Design.CardHighlight,
            unselectedContainerColor = Color.Transparent,
        ),
        modifier = Modifier.padding(NavigationDrawerItemDefaults.ItemPadding),
    )
}
