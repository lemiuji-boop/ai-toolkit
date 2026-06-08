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

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.ui.design.NtiV2Design
import ru.nti.sbor.ui.design.NtiV2PrimaryButton
import ru.nti.sbor.ui.design.NtiV2TextField
import ru.nti.sbor.ui.theme.NtiTokens

/** Форма записи — дизайн v2. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordFormScreenV2(
    state: RecordFormUiState,
    viewModel: RecordFormViewModel,
    onBack: () -> Unit,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        if (state.recordId == null) "Новая запись" else "Редактирование",
                        color = NtiV2Design.TextPrimary,
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад",
                            tint = NtiV2Design.TextPrimary,
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = NtiV2Design.Surface),
            )
        },
        containerColor = NtiV2Design.Surface,
    ) { padding ->
        if (state.isLoading) {
            Text(
                "Загрузка…",
                color = NtiV2Design.TextMuted,
                modifier = Modifier.padding(padding).padding(NtiTokens.SpacingMd),
            )
            return@Scaffold
        }
        Column(
            Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState())
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            V2OperationDropdown(state, viewModel)
            if (state.isOtherOperation) {
                NtiV2TextField(
                    value = state.otherOperationText,
                    onValueChange = { viewModel.update { s -> s.copy(otherOperationText = it) } },
                    label = "Название операции",
                    isError = state.otherOperationError,
                )
            }
            NtiV2TextField(
                value = state.product,
                onValueChange = { viewModel.update { s -> s.copy(product = it) } },
                label = "Изделие / зав. №",
                isError = state.productError,
            )
            NtiV2TextField(
                value = state.valueText,
                onValueChange = { viewModel.update { s -> s.copy(valueText = it) } },
                label = "Значение",
                isError = state.valueError,
            )
            V2UnitDropdown(state, viewModel)
            NtiV2TextField(
                value = state.dateText,
                onValueChange = { viewModel.update { s -> s.copy(dateText = it) } },
                label = "Дата (ДД.ММ.ГГГГ)",
            )
            NtiV2TextField(
                value = state.worker,
                onValueChange = { viewModel.update { s -> s.copy(worker = it) } },
                label = "Исполнитель",
                isError = state.workerError,
            )
            NtiV2TextField(
                value = state.note,
                onValueChange = { viewModel.update { s -> s.copy(note = it) } },
                label = "Примечание",
                singleLine = false,
            )
            NtiV2PrimaryButton("Сохранить", onClick = { viewModel.save() })
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun V2OperationDropdown(state: RecordFormUiState, viewModel: RecordFormViewModel) {
    var expanded by remember { mutableStateOf(false) }
    val options = state.operations + OTHER_OPERATION_LABEL
    val fieldColors = v2DropdownColors()
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = if (state.isOtherOperation) OTHER_OPERATION_LABEL else state.selectedOperation,
            onValueChange = {},
            readOnly = true,
            label = { Text("Операция", color = NtiV2Design.TextSecondary) },
            isError = state.operationError,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
            colors = fieldColors,
        )
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            options.forEach { op ->
                DropdownMenuItem(
                    text = { Text(op) },
                    onClick = {
                        expanded = false
                        viewModel.update {
                            it.copy(selectedOperation = op, isOtherOperation = op == OTHER_OPERATION_LABEL)
                        }
                    },
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun V2UnitDropdown(state: RecordFormUiState, viewModel: RecordFormViewModel) {
    var expanded by remember { mutableStateOf(false) }
    val fieldColors = v2DropdownColors()
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = state.unit.label,
            onValueChange = {},
            readOnly = true,
            label = { Text("Единица", color = NtiV2Design.TextSecondary) },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
            colors = fieldColors,
        )
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            LaborUnit.entries.forEach { unit ->
                DropdownMenuItem(
                    text = { Text(unit.label) },
                    onClick = {
                        expanded = false
                        viewModel.update { it.copy(unit = unit) }
                    },
                )
            }
        }
    }
}

@Composable
private fun v2DropdownColors() = OutlinedTextFieldDefaults.colors(
    focusedBorderColor = NtiV2Design.AccentBlue,
    unfocusedBorderColor = NtiV2Design.Border,
    focusedTextColor = NtiV2Design.TextPrimary,
    unfocusedTextColor = NtiV2Design.TextPrimary,
    cursorColor = NtiV2Design.AccentBlue,
)
