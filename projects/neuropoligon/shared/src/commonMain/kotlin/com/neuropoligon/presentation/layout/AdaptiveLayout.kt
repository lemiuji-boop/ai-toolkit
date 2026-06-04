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

package com.neuropoligon.presentation.layout

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

public enum class WindowSizeClass {
    Compact,
    Medium,
    Expanded,
}

@Composable
public fun AdaptiveContent(
    modifier: Modifier = Modifier,
    maxContentWidth: Dp = 900.dp,
    content: @Composable (WindowSizeClass) -> Unit,
) {
    BoxWithConstraints(modifier = modifier.fillMaxWidth()) {
        val sizeClass = when {
            maxWidth < 600.dp -> WindowSizeClass.Compact
            maxWidth < 840.dp -> WindowSizeClass.Medium
            else -> WindowSizeClass.Expanded
        }
        val horizontalPadding = when (sizeClass) {
            WindowSizeClass.Compact -> 16.dp
            WindowSizeClass.Medium -> 24.dp
            WindowSizeClass.Expanded -> 32.dp
        }
        Box(
            Modifier
                .fillMaxWidth()
                .padding(horizontal = horizontalPadding)
                .widthIn(max = maxContentWidth),
        ) {
            content(sizeClass)
        }
    }
}
