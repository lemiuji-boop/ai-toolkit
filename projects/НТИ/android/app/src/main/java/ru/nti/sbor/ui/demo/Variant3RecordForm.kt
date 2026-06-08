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

package ru.nti.sbor.ui.demo

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ru.nti.sbor.ui.theme.NtiTokens

/** Макет 3: форма новой записи (mockup_03_record_form). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun Variant3RecordFormScreen() {
    val scroll = rememberScrollState()
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Новая запись", fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = {}) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Назад",
                            tint = Color.White,
                        )
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
                onClick = {},
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(NtiTokens.SpacingMd),
                shape = RoundedCornerShape(NtiTokens.RadiusMd),
                colors = ButtonDefaults.buttonColors(containerColor = NtiTokens.AccentSteelBlue),
            ) {
                Icon(Icons.Default.Check, contentDescription = null, tint = Color.White)
                Text("Сохранить", Modifier.padding(start = NtiTokens.SpacingSm), color = Color.White)
            }
        },
        containerColor = Color.White,
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .verticalScroll(scroll)
                .padding(NtiTokens.SpacingMd),
            verticalArrangement = Arrangement.spacedBy(NtiTokens.SpacingMd),
        ) {
            OutlinedTextField(
                value = "Токарная",
                onValueChange = {},
                label = { Text("Операция") },
                modifier = Modifier.fillMaxWidth(),
                readOnly = true,
            )
            OutlinedTextField(
                value = "",
                onValueChange = {},
                label = { Text("Изделие") },
                modifier = Modifier.fillMaxWidth(),
                readOnly = true,
            )
            OutlinedTextField(
                value = "1,25",
                onValueChange = {},
                label = { Text("Значение") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = "н/ч",
                onValueChange = {},
                label = { Text("Единица") },
                modifier = Modifier.fillMaxWidth(),
                readOnly = true,
            )
            OutlinedTextField(
                value = "04.06.2026",
                onValueChange = {},
                label = { Text("Дата") },
                modifier = Modifier.fillMaxWidth(),
                trailingIcon = {
                    Icon(Icons.Default.Info, contentDescription = "Календарь")
                },
            )
            OutlinedTextField(
                value = "Иванов",
                onValueChange = {},
                label = { Text("Исполнитель") },
                modifier = Modifier.fillMaxWidth(),
                readOnly = true,
            )
            OutlinedTextField(
                value = "",
                onValueChange = {},
                label = { Text("Примечание") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(120.dp),
                minLines = 4,
            )
            Spacer(Modifier.height(80.dp))
        }
    }
}
