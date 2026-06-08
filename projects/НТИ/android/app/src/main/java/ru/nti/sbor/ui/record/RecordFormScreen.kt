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

package ru.nti.sbor.ui.record

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import ru.nti.sbor.ui.design.AppDesignVariant

@Composable
fun RecordFormScreen(
    viewModel: RecordFormViewModel,
    designVariant: AppDesignVariant,
    onBack: () -> Unit,
) {
    val state by viewModel.state.collectAsState()
    LaunchedEffect(state.saved) {
        if (state.saved) onBack()
    }
    when (designVariant) {
        AppDesignVariant.V3_FORM -> RecordFormScreenV3(state, viewModel, onBack)
        AppDesignVariant.V2_DARK_HOME -> RecordFormScreenV2(state, viewModel, onBack)
        else -> RecordFormScreenStandard(state, viewModel, onBack)
    }
}
