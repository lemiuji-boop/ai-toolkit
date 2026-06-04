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

package com.neuropoligon.presentation.lesson

import androidx.compose.material3.ColorScheme
import androidx.compose.ui.graphics.Color
import com.neuropoligon.domain.settings.ReaderColorTone

public data class LessonReaderPalette(
    val background: Color,
    val onBackground: Color,
    val surface: Color,
    val onSurface: Color,
    val accent: Color,
    val importantContainer: Color,
    val importantOn: Color,
    val templateContainer: Color,
    val templateOn: Color,
    val promptContainer: Color,
    val promptOn: Color,
)

public fun readerPalette(base: ColorScheme, tone: ReaderColorTone): LessonReaderPalette = when (tone) {
    ReaderColorTone.Day -> LessonReaderPalette(
        background = Color(0xFFF8FAFC),
        onBackground = Color(0xFF0F172A),
        surface = Color(0xFFFFFFFF),
        onSurface = Color(0xFF0F172A),
        accent = base.primary,
        importantContainer = Color(0xFFFEF3C7),
        importantOn = Color(0xFF78350F),
        templateContainer = Color(0xFFE0E7FF),
        templateOn = Color(0xFF312E81),
        promptContainer = Color(0xFFECFDF5),
        promptOn = Color(0xFF065F46),
    )
    ReaderColorTone.Night -> LessonReaderPalette(
        background = Color(0xFF0B1220),
        onBackground = Color(0xFFE2E8F0),
        surface = Color(0xFF1E293B),
        onSurface = Color(0xFFF1F5F9),
        accent = Color(0xFF93C5FD),
        importantContainer = Color(0xFF422006),
        importantOn = Color(0xFFFDE68A),
        templateContainer = Color(0xFF1E1B4B),
        templateOn = Color(0xFFC7D2FE),
        promptContainer = Color(0xFF064E3B),
        promptOn = Color(0xFFA7F3D0),
    )
    ReaderColorTone.Warm -> LessonReaderPalette(
        background = Color(0xFFFFFBEB),
        onBackground = Color(0xFF422006),
        surface = Color(0xFFFFF7ED),
        onSurface = Color(0xFF431407),
        accent = Color(0xFFEA580C),
        importantContainer = Color(0xFFFFEDD5),
        importantOn = Color(0xFF7C2D12),
        templateContainer = Color(0xFFFED7AA),
        templateOn = Color(0xFF7C2D12),
        promptContainer = Color(0xFFFFF1F2),
        promptOn = Color(0xFF881337),
    )
    ReaderColorTone.Cool -> LessonReaderPalette(
        background = Color(0xFFF0F9FF),
        onBackground = Color(0xFF0C4A6E),
        surface = Color(0xFFE0F2FE),
        onSurface = Color(0xFF075985),
        accent = Color(0xFF0284C7),
        importantContainer = Color(0xFFBAE6FD),
        importantOn = Color(0xFF0C4A6E),
        templateContainer = Color(0xFFDBEAFE),
        templateOn = Color(0xFF1E3A8A),
        promptContainer = Color(0xFFCCFBF1),
        promptOn = Color(0xFF134E4A),
    )
}
