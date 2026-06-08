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

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import ru.nti.sbor.NtiSborApp
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.design.AppDesignVariant

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val container = (application as NtiSborApp).container
        val designVariant = AppDesignVariant.fromBuildConfig()
        val savedTheme = runBlocking { container.appPreferences.themeMode.first() }
        val initialTheme = when (designVariant) {
            AppDesignVariant.V2_DARK_HOME -> ThemeMode.DARK
            AppDesignVariant.V1_LIGHT_HOME,
            AppDesignVariant.V3_FORM,
            AppDesignVariant.V4_SETTINGS,
            -> ThemeMode.LIGHT
            AppDesignVariant.STANDARD -> ThemeMode.DARK
        }

        setContent {
            NtiAppNavHost(
                container = container,
                designVariant = designVariant,
                initialTheme = initialTheme,
            )
        }
    }
}
