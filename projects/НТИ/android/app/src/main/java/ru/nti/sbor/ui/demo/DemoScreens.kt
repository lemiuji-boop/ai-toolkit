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

package ru.nti.sbor.ui.demo

import androidx.compose.runtime.Composable
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.theme.NtiSborTheme

/** Корневой экран демо-сборки по номеру макета (1–4). */
@Composable
fun DemoSignoffApp(demoIndex: Int) {
    when (demoIndex) {
        1 -> NtiSborTheme(themeMode = ThemeMode.LIGHT) { Variant1HomeLightScreen() }
        2 -> NtiSborTheme(themeMode = ThemeMode.DARK) { Variant2HomeDarkScreen() }
        3 -> NtiSborTheme(themeMode = ThemeMode.LIGHT) { Variant3RecordFormScreen() }
        4 -> NtiSborTheme(themeMode = ThemeMode.LIGHT) { Variant4SettingsScreen() }
        else -> NtiSborTheme(themeMode = ThemeMode.LIGHT) { Variant1HomeLightScreen() }
    }
}
