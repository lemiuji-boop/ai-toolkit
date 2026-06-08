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
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
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
import androidx.compose.ui.text.font.FontWeight
import ru.nti.sbor.domain.model.LaborUnit
import ru.nti.sbor.ui.theme.NtiTokens

/** Форма записи — дизайн v3, полная функциональность. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecordFormScreenV3(
    state: RecordFormUiState,
    viewModel: RecordFormViewModel,
    onBack: () -> Unit,
) {
    val scroll = rememberScrollState()
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        if (state.recordId == null) "Новая запись" else "Редактирование",
                        fontWeight = FontWeight.SemiBold,
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Назад", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = NtiTokens.AccentSteelBlue,
                    titleContentColor = Color.White,
                ),
            )
        },
        bottomBar = {
            Button(
                onClick = { viewModel.save() },
                modifier = Modifier.fillMaxWidth().padding(NtiTokens.SpacingMd),
                shape = RoundedCornerShape(NtiTokens.RadiusMd),
                colors = ButtonDefaults.buttonColors(containerColor = NtiTokens.AccentSteelBlue),
            ) {
                Icon(Icons.Default.Check, contentDescription = null, tint = Color.White)
                Text("Сохранить", Modifier.padding(start = NtiTokens.SpacingSm), color = Color.White)
            }
        },
        containerColor = Color.White,
    ) { padding ->
        if (state.isLoading) {
            Text("Загрузка…", Modifier.padding(padding).padding(NtiTokens.SpacingMd))
            return@Scaffold
        }
        Column(
            Modifier.padding(padding).verticalScroll(scroll).padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            V3OperationDropdown(state, viewModel)
            if (state.isOtherOperation) {
                OutlinedTextField(
                    value = state.otherOperationText,
                    onValueChange = { viewModel.update { s -> s.copy(otherOperationText = it) } },
                    label = { Text("Название операции") },
                    isError = state.otherOperationError,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            OutlinedTextField(
                value = state.product,
                onValueChange = { viewModel.update { s -> s.copy(product = it) } },
                label = { Text("Изделие") },
                isError = state.productError,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.valueText,
                onValueChange = { viewModel.update { s -> s.copy(valueText = it) } },
                label = { Text("Значение") },
                isError = state.valueError,
                modifier = Modifier.fillMaxWidth(),
            )
            V3UnitDropdown(state, viewModel)
            OutlinedTextField(
                value = state.dateText,
                onValueChange = { viewModel.update { s -> s.copy(dateText = it) } },
                label = { Text("Дата") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.worker,
                onValueChange = { viewModel.update { s -> s.copy(worker = it) } },
                label = { Text("Исполнитель") },
                isError = state.workerError,
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.note,
                onValueChange = { viewModel.update { s -> s.copy(note = it) } },
                label = { Text("Примечание") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3,
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun V3OperationDropdown(state: RecordFormUiState, viewModel: RecordFormViewModel) {
    var expanded by remember { mutableStateOf(false) }
    val options = state.operations + OTHER_OPERATION_LABEL
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = if (state.isOtherOperation) OTHER_OPERATION_LABEL else state.selectedOperation,
            onValueChange = {},
            readOnly = true,
            label = { Text("Операция") },
            isError = state.operationError,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
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
private fun V3UnitDropdown(state: RecordFormUiState, viewModel: RecordFormViewModel) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }) {
        OutlinedTextField(
            value = state.unit.label,
            onValueChange = {},
            readOnly = true,
            label = { Text("Единица") },
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            modifier = Modifier.menuAnchor().fillMaxWidth(),
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
