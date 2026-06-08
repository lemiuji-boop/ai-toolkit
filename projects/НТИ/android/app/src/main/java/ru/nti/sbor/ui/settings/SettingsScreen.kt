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

package ru.nti.sbor.ui.settings

import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import ru.nti.sbor.ui.design.AppDesignVariant

@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel,
    designVariant: AppDesignVariant,
    onBack: () -> Unit,
) {
    val state by viewModel.state.collectAsState()
    val snackbar = remember { SnackbarHostState() }

    LaunchedEffect(state.message) {
        state.message?.let { snackbar.showSnackbar(it) }
    }

    when (designVariant) {
        AppDesignVariant.V2_DARK_HOME -> SettingsScreenV2(
            state = state,
            snackbarHostState = snackbar,
            onBack = onBack,
            onThemeSelect = viewModel::setTheme,
            onFontScaleSelect = viewModel::setFontScale,
            onHighContrastChange = viewModel::setHighContrast,
            onLargeTouchChange = viewModel::setLargeTouch,
        )
        else -> SettingsScreenV2(
            state = state,
            snackbarHostState = snackbar,
            onBack = onBack,
            onThemeSelect = viewModel::setTheme,
            onFontScaleSelect = viewModel::setFontScale,
            onHighContrastChange = viewModel::setHighContrast,
            onLargeTouchChange = viewModel::setLargeTouch,
        )
    }
}
