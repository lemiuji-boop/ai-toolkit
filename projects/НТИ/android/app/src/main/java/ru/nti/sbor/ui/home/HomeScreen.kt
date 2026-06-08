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

package ru.nti.sbor.ui.home

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import ru.nti.sbor.ui.design.AppDesignVariant

@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    designVariant: AppDesignVariant,
    onAdd: () -> Unit,
    onEdit: (Long) -> Unit,
    onSettings: () -> Unit,
    onOpenMenu: () -> Unit = onSettings,
) {
    val state by viewModel.uiState.collectAsState()
    val onDelete: (Long) -> Unit = { id -> viewModel.deleteRecord(id) {} }

    when (designVariant) {
        AppDesignVariant.V1_LIGHT_HOME -> HomeScreenV1(
            state = state,
            onSearchChange = viewModel::onSearchChange,
            onAdd = onAdd,
            onEdit = onEdit,
            onSettings = onSettings,
            onDelete = onDelete,
        )
        AppDesignVariant.V2_DARK_HOME -> HomeScreenV2(
            state = state,
            onSearchChange = viewModel::onSearchChange,
            onAdd = onAdd,
            onEdit = onEdit,
            onOpenMenu = onOpenMenu,
            onSettings = onSettings,
            onDelete = onDelete,
        )
        else -> HomeScreenStandard(
            state = state,
            onSearchChange = viewModel::onSearchChange,
            onAdd = onAdd,
            onEdit = onEdit,
            onSettings = onSettings,
            onDelete = onDelete,
        )
    }
}
