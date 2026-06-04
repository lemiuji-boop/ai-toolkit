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

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList

/**
 * Простой стек навигации без androidx.navigation (совместим с Wasm).
 */
public class AppNavigator {
    private val backStack: SnapshotStateList<NavDestination> = mutableStateListOf(NavDestination.Onboarding)
    public var current: NavDestination by mutableStateOf(NavDestination.Onboarding)
        private set

    public fun navigate(destination: NavDestination) {
        backStack.add(destination)
        current = destination
    }

    public fun pop(): Boolean {
        if (backStack.size <= 1) return false
        backStack.removeAt(backStack.lastIndex)
        current = backStack.last()
        return true
    }

    public fun resetTo(destination: NavDestination) {
        backStack.clear()
        backStack.add(destination)
        current = destination
    }
}

public sealed class NavDestination {
    public data object Onboarding : NavDestination()
    public data object Home : NavDestination()
    public data class Modules(val trackId: String) : NavDestination()
    public data class Lesson(val trackId: String, val moduleId: String) : NavDestination()
    public data object Settings : NavDestination()
    public data object Auth : NavDestination()
    public data object Resources : NavDestination()
    public data object Review : NavDestination()
    public data class CourseOutline(val trackId: String) : NavDestination()
}

@Composable
public fun rememberAppNavigator(): AppNavigator {
    return androidx.compose.runtime.remember { AppNavigator() }
}
