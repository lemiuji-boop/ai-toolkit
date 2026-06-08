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

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import ru.nti.sbor.ui.theme.NtiTokens

/** Общие токены и компоненты дизайна v2 (тёмный дашборд). */
object NtiV2Design {
    val Surface = Color(0xFF121418)
    val CardBg = Color(0xFF1E2329)
    val CardHighlight = Color(0xFF243044)
    val AccentBlue = Color(0xFF4A9FE8)
    val TextPrimary = Color.White
    val TextMuted = Color(0xFF8A939E)
    val TextSecondary = Color(0xFFB0B8C4)
    val Border = Color(0xFF3A4555)
    val Error = Color(0xFFE57373)
    val Success = Color(0xFF81C784)
}

@Composable
fun NtiV2BrandTitle(modifier: Modifier = Modifier) {
    Text(
        buildAnnotatedString {
            withStyle(SpanStyle(color = NtiV2Design.TextPrimary)) { append("НТИ.") }
            withStyle(SpanStyle(color = NtiV2Design.AccentBlue, fontWeight = FontWeight.Bold)) {
                append("Сбор")
            }
        },
        modifier = modifier,
    )
}

@Composable
fun NtiV2SectionCard(
    title: String,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = NtiV2Design.CardHighlight),
        shape = RoundedCornerShape(NtiTokens.RadiusMd),
    ) {
        Column(Modifier.padding(NtiTokens.SpacingMd)) {
            Text(title, color = NtiV2Design.TextPrimary, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(NtiTokens.SpacingSm))
            content()
        }
    }
}

@Composable
fun NtiV2TextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    isError: Boolean = false,
    singleLine: Boolean = true,
    visualTransformation: VisualTransformation = VisualTransformation.None,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier.fillMaxWidth(),
        label = { Text(label, color = NtiV2Design.TextSecondary) },
        placeholder = if (placeholder.isNotEmpty()) {
            { Text(placeholder, color = NtiV2Design.TextMuted) }
        } else {
            null
        },
        isError = isError,
        singleLine = singleLine,
        visualTransformation = visualTransformation,
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = NtiV2Design.AccentBlue,
            unfocusedBorderColor = NtiV2Design.Border,
            focusedTextColor = NtiV2Design.TextPrimary,
            unfocusedTextColor = NtiV2Design.TextPrimary,
            cursorColor = NtiV2Design.AccentBlue,
            focusedLabelColor = NtiV2Design.AccentBlue,
            unfocusedLabelColor = NtiV2Design.TextMuted,
        ),
        shape = RoundedCornerShape(NtiTokens.RadiusMd),
    )
}

@Composable
fun NtiV2PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = NtiV2Design.AccentBlue,
            contentColor = Color.White,
            disabledContainerColor = NtiV2Design.Border,
        ),
        shape = RoundedCornerShape(NtiTokens.RadiusMd),
    ) {
        Text(text, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
fun NtiV2SecondaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth(),
        enabled = enabled,
        colors = ButtonDefaults.buttonColors(
            containerColor = NtiV2Design.CardBg,
            contentColor = NtiV2Design.AccentBlue,
        ),
        shape = RoundedCornerShape(NtiTokens.RadiusMd),
    ) {
        Text(text)
    }
}
