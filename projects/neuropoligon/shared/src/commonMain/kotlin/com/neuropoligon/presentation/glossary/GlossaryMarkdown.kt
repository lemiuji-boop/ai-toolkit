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

package com.neuropoligon.presentation.glossary

import androidx.compose.foundation.text.ClickableText
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import com.neuropoligon.domain.content.GlossaryEntry
import com.neuropoligon.platform.openUrl

private const val TERM_TAG = "TERM"
private const val URL_TAG = "URL"

private val termPattern = Regex("""\[\[([^|\]]+)(?:\|([^\]]+))?\]\]""")
private val linkPattern = Regex("""\[([^\]]+)]\((https?://[^)]+)\)""")

@Composable
public fun GlossaryMarkdown(
    markdown: String,
    entries: List<GlossaryEntry>,
    modifier: Modifier = Modifier,
) {
    var selected by remember { mutableStateOf<GlossaryEntry?>(null) }
    val textColor = MaterialTheme.colorScheme.onSurface
    val accentColor = MaterialTheme.colorScheme.primary
    val bodyStyle = MaterialTheme.typography.bodyLarge.copy(color = textColor)
    val paragraphs = remember(markdown) { markdown.split("\n\n").filter { it.isNotBlank() } }

    Column(modifier, verticalArrangement = Arrangement.spacedBy(10.dp)) {
        paragraphs.forEach { paragraph ->
            LessonParagraph(
                text = paragraph.trim(),
                entries = entries,
                bodyStyle = bodyStyle,
                accentColor = accentColor,
                onTermClick = { selected = it },
            )
        }
    }

    selected?.let { entry ->
        AlertDialog(
            onDismissRequest = { selected = null },
            title = { Text(entry.term, color = MaterialTheme.colorScheme.onSurface) },
            text = {
                Column {
                    Text(entry.naiveDefinition, color = MaterialTheme.colorScheme.onSurface)
                    entry.fullDefinition?.let {
                        Text(
                            it,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(top = 8.dp),
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { selected = null }) { Text("Закрыть") }
            },
        )
    }
}

@Composable
private fun LessonParagraph(
    text: String,
    entries: List<GlossaryEntry>,
    bodyStyle: androidx.compose.ui.text.TextStyle,
    accentColor: androidx.compose.ui.graphics.Color,
    onTermClick: (GlossaryEntry) -> Unit,
) {
    val lines = text.split("\n")
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        lines.forEach { line ->
            val trimmed = line.trim()
            when {
                trimmed.startsWith("## ") -> Text(
                    trimmed.removePrefix("## "),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                trimmed.startsWith("**") && trimmed.endsWith("**") -> Text(
                    trimmed.removeSurrounding("**"),
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                trimmed.startsWith("- ") -> InlineMarkdownLine(
                    text = trimmed.removePrefix("- "),
                    entries = entries,
                    bodyStyle = bodyStyle,
                    accentColor = accentColor,
                    onTermClick = onTermClick,
                )
                trimmed.isNotEmpty() -> InlineMarkdownLine(
                    text = trimmed,
                    entries = entries,
                    bodyStyle = bodyStyle,
                    accentColor = accentColor,
                    onTermClick = onTermClick,
                )
            }
        }
    }
}

@Composable
private fun InlineMarkdownLine(
    text: String,
    entries: List<GlossaryEntry>,
    bodyStyle: androidx.compose.ui.text.TextStyle,
    accentColor: androidx.compose.ui.graphics.Color,
    onTermClick: (GlossaryEntry) -> Unit,
) {
    val parts = remember(text) { splitParts(text) }
    val annotated = remember(parts) {
        buildAnnotatedString {
            val base = bodyStyle.toSpanStyle()
            val accent = base.copy(color = accentColor, fontWeight = FontWeight.SemiBold)
            val linkStyle = base.copy(color = accentColor, textDecoration = TextDecoration.Underline)
            parts.forEach { part ->
                when (part) {
                    is RenderPart.Text -> withStyle(base) { append(part.value) }
                    is RenderPart.Term -> {
                        pushStringAnnotation(tag = TERM_TAG, annotation = part.id)
                        withStyle(accent) { append(part.label) }
                        pop()
                    }
                    is RenderPart.Link -> {
                        pushStringAnnotation(tag = URL_TAG, annotation = part.url)
                        withStyle(linkStyle) { append(part.label) }
                        pop()
                    }
                }
            }
        }
    }

    ClickableText(
        text = annotated,
        style = bodyStyle,
        onClick = { offset ->
            annotated.getStringAnnotations(TERM_TAG, offset, offset).firstOrNull()?.item?.let { id ->
                entries.find { entry ->
                    entry.id.equals(id, ignoreCase = true) ||
                        entry.term.equals(id, ignoreCase = true) ||
                        entry.aliases.any { alias -> alias.equals(id, ignoreCase = true) }
                }?.let(onTermClick)
            }
            annotated.getStringAnnotations(URL_TAG, offset, offset).firstOrNull()?.item?.let { url ->
                openUrl(url)
            }
        },
    )
}

private sealed interface RenderPart {
    data class Text(val value: String) : RenderPart
    data class Term(val id: String, val label: String) : RenderPart
    data class Link(val label: String, val url: String) : RenderPart
}

private fun splitParts(markdown: String): List<RenderPart> {
    val termParts = splitTerms(markdown)
    val final = mutableListOf<RenderPart>()
    termParts.forEach { part ->
        when (part) {
            is RenderPart.Text -> final += splitLinks(part.value)
            else -> final += part
        }
    }
    return final
}

private fun splitTerms(markdown: String): List<RenderPart> {
    val result = mutableListOf<RenderPart>()
    var last = 0
    termPattern.findAll(markdown).forEach { match ->
        if (match.range.first > last) result.add(RenderPart.Text(markdown.substring(last, match.range.first)))
        val id = match.groupValues[1]
        val label = match.groupValues.getOrNull(2)?.ifBlank { null } ?: id
        result.add(RenderPart.Term(id, label))
        last = match.range.last + 1
    }
    if (last < markdown.length) result.add(RenderPart.Text(markdown.substring(last)))
    return result
}

private fun splitLinks(text: String): List<RenderPart> {
    val result = mutableListOf<RenderPart>()
    var last = 0
    linkPattern.findAll(text).forEach { match ->
        if (match.range.first > last) result.add(RenderPart.Text(text.substring(last, match.range.first)))
        result.add(RenderPart.Link(label = match.groupValues[1], url = match.groupValues[2]))
        last = match.range.last + 1
    }
    if (last < text.length) result.add(RenderPart.Text(text.substring(last)))
    return result
}
