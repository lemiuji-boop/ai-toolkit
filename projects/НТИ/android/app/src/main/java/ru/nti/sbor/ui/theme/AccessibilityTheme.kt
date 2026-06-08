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

package ru.nti.sbor.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import ru.nti.sbor.data.settings.AccessibilityPrefs
import ru.nti.sbor.ui.design.NtiV2Design

val LocalAccessibilityPrefs = staticCompositionLocalOf { AccessibilityPrefs() }

@Composable
fun NtiAccessibilityProvider(
    prefs: AccessibilityPrefs,
    content: @Composable () -> Unit,
) {
    CompositionLocalProvider(LocalAccessibilityPrefs provides prefs) {
        val scaledTypography = scaleTypography(NtiTypography, prefs.fontScale)
        MaterialTheme(typography = scaledTypography) {
            content()
        }
    }
}

private fun scaleTypography(base: Typography, scale: Float): Typography {
    if (scale == 1f) return base
    return Typography(
        displayLarge = base.displayLarge.copy(fontSize = base.displayLarge.fontSize * scale),
        displayMedium = base.displayMedium.copy(fontSize = base.displayMedium.fontSize * scale),
        displaySmall = base.displaySmall.copy(fontSize = base.displaySmall.fontSize * scale),
        headlineLarge = base.headlineLarge.copy(fontSize = base.headlineLarge.fontSize * scale),
        headlineMedium = base.headlineMedium.copy(fontSize = base.headlineMedium.fontSize * scale),
        headlineSmall = base.headlineSmall.copy(fontSize = base.headlineSmall.fontSize * scale),
        titleLarge = base.titleLarge.copy(fontSize = base.titleLarge.fontSize * scale),
        titleMedium = base.titleMedium.copy(fontSize = base.titleMedium.fontSize * scale),
        titleSmall = base.titleSmall.copy(fontSize = base.titleSmall.fontSize * scale),
        bodyLarge = base.bodyLarge.copy(fontSize = base.bodyLarge.fontSize * scale),
        bodyMedium = base.bodyMedium.copy(fontSize = base.bodyMedium.fontSize * scale),
        bodySmall = base.bodySmall.copy(fontSize = base.bodySmall.fontSize * scale),
        labelLarge = base.labelLarge.copy(fontSize = base.labelLarge.fontSize * scale),
        labelMedium = base.labelMedium.copy(fontSize = base.labelMedium.fontSize * scale),
        labelSmall = base.labelSmall.copy(fontSize = base.labelSmall.fontSize * scale),
    )
}

/** Цвета v2 с учётом режима высокого контраста. */
object AccessibleV2Colors {
    @Composable
    fun surface(): Color = if (LocalAccessibilityPrefs.current.highContrast) Color.Black else NtiV2Design.Surface

    @Composable
    fun textPrimary(): Color =
        if (LocalAccessibilityPrefs.current.highContrast) Color.White else NtiV2Design.TextPrimary

    @Composable
    fun accent(): Color =
        if (LocalAccessibilityPrefs.current.highContrast) Color(0xFFFFEB3B) else NtiV2Design.AccentBlue
}

/** Минимальный размер зоны нажатия с учётом настроек. */
@Composable
fun accessibleMinTouchTarget(): androidx.compose.ui.unit.Dp {
    val prefs = LocalAccessibilityPrefs.current
    return if (prefs.largeTouchTargets) 56.dp else NtiTokens.MinTouchTarget
}
