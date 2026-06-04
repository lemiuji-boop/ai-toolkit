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

package com.neuropoligon.presentation.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

private val LightColors = lightColorScheme(
    primary = NeuroColors.AiIndigo,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0E7FF),
    onPrimaryContainer = Color(0xFF312E81),
    secondary = NeuroColors.AiCyan,
    onSecondary = Color(0xFF083344),
    tertiary = NeuroColors.AiViolet,
    onTertiary = Color.White,
    background = Color(0xFFF7F7FC),
    onBackground = Color(0xFF11132A),
    surface = Color(0xFFFFFFFF),
    onSurface = Color(0xFF11132A),
    surfaceVariant = Color(0xFFE2E8F0),
    onSurfaceVariant = Color(0xFF475569),
    surfaceContainerLow = Color(0xFFFFFFFF),
    surfaceContainerHigh = Color(0xFFE2E8F0),
    error = Color(0xFFDC2626),
    errorContainer = NeuroColors.ErrorContainerLight,
    onErrorContainer = NeuroColors.ErrorOnContainerLight,
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFA5B4FC),
    onPrimary = Color(0xFF1E1B4B),
    primaryContainer = Color(0xFF3730A3),
    onPrimaryContainer = Color(0xFFE0E7FF),
    secondary = Color(0xFF67E8F9),
    onSecondary = Color(0xFF083344),
    tertiary = Color(0xFFC4B5FD),
    onTertiary = Color(0xFF2E1065),
    background = Color(0xFF11132A),
    onBackground = Color(0xFFFFFFFF),
    surface = Color(0xFF1E293B),
    onSurface = Color(0xFFF7F7FC),
    surfaceVariant = Color(0xFF334155),
    onSurfaceVariant = Color(0xFFCBD5E1),
    surfaceContainerLow = Color(0xFF1E293B),
    surfaceContainerHigh = Color(0xFF334155),
    error = Color(0xFFF87171),
    errorContainer = Color(0xFF7F1D1D),
    onErrorContainer = Color(0xFFFECACA),
)

private val NeuroShapes = Shapes(
    extraSmall = RoundedCornerShape(10.dp),
    small = RoundedCornerShape(14.dp),
    medium = RoundedCornerShape(36.dp),
    large = RoundedCornerShape(36.dp),
    extraLarge = RoundedCornerShape(36.dp),
)

@Composable
public fun NeuropoligonTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) DarkColors else LightColors,
        typography = NeuroTypography,
        shapes = NeuroShapes,
        content = content,
    )
}
