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

package ru.nti.sbor.ui.design

import androidx.compose.runtime.compositionLocalOf
import ru.nti.sbor.BuildConfig

/** Вариант визуального оформления (1–4 для демо-сборок). */
enum class AppDesignVariant {
    V1_LIGHT_HOME,
    V2_DARK_HOME,
    V3_FORM,
    V4_SETTINGS,
    STANDARD,
    ;

    fun usesV2Chrome(): Boolean = this == V2_DARK_HOME

    companion object {
        fun fromBuildConfig(): AppDesignVariant = when (BuildConfig.DEMO_INDEX) {
            1 -> V1_LIGHT_HOME
            2, 0 -> V2_DARK_HOME
            3 -> V3_FORM
            4 -> V4_SETTINGS
            else -> V2_DARK_HOME
        }
    }
}

val LocalAppDesignVariant = compositionLocalOf { AppDesignVariant.STANDARD }
