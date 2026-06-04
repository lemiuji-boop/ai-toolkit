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

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.ClickableText
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.neuropoligon.domain.content.GlossaryEntry
import com.neuropoligon.platform.openUrl

private const val TERM_TAG = "TERM"
private const val URL_TAG = "URL"
private val termPattern = Regex("""\[\[([^|\]]+)(?:\|([^\]]+))?\]\]""")
private val linkPattern = Regex("""\[([^\]]+)]\((https?://[^)]+)\)""")

@Composable
public fun LessonRichMarkdown(
    markdown: String,
    entries: List<GlossaryEntry>,
    palette: LessonReaderPalette,
    fontScale: Float,
    modifier: Modifier = Modifier,
) {
    val blocks = remember(markdown) { parseBlocks(markdown) }
    val baseSize = (16f * fontScale).sp

    Column(modifier, verticalArrangement = Arrangement.spacedBy(14.dp)) {
        blocks.forEach { block ->
            when (block) {
                is MarkdownBlock.Heading -> Text(
                    block.text,
                    style = MaterialTheme.typography.titleLarge.copy(
                        fontSize = (22f * fontScale).sp,
                        fontWeight = FontWeight.Bold,
                        color = palette.onBackground,
                    ),
                    modifier = Modifier.padding(top = 8.dp),
                )
                is MarkdownBlock.Subheading -> Text(
                    block.text,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontSize = (18f * fontScale).sp,
                        fontWeight = FontWeight.SemiBold,
                        color = palette.accent,
                    ),
                )
                is MarkdownBlock.Divider -> HorizontalDivider(
                    modifier = Modifier.padding(vertical = 6.dp),
                    color = palette.accent.copy(alpha = 0.35f),
                )
                is MarkdownBlock.Important -> StyledBox(
                    text = block.text,
                    container = palette.importantContainer,
                    onContainer = palette.importantOn,
                    fontScale = fontScale,
                    fontWeight = FontWeight.SemiBold,
                )
                is MarkdownBlock.Template -> StyledBox(
                    text = block.text,
                    container = palette.templateContainer,
                    onContainer = palette.templateOn,
                    fontScale = fontScale,
                    fontStyle = FontStyle.Italic,
                )
                is MarkdownBlock.Prompt -> StyledBox(
                    text = block.text,
                    container = palette.promptContainer,
                    onContainer = palette.promptOn,
                    fontScale = fontScale,
                    mono = true,
                )
                is MarkdownBlock.Bullet -> InlineRichText(
                    text = "• ${block.text}",
                    entries = entries,
                    color = palette.onSurface,
                    accent = palette.accent,
                    fontSize = baseSize,
                    fontWeight = FontWeight.Normal,
                )
                is MarkdownBlock.Paragraph -> InlineRichText(
                    text = block.text,
                    entries = entries,
                    color = palette.onSurface,
                    accent = palette.accent,
                    fontSize = baseSize,
                    fontWeight = if (block.bold) FontWeight.Bold else FontWeight.Normal,
                    fontStyle = if (block.italic) FontStyle.Italic else FontStyle.Normal,
                )
            }
        }
    }
}

@Composable
private fun StyledBox(
    text: String,
    container: androidx.compose.ui.graphics.Color,
    onContainer: androidx.compose.ui.graphics.Color,
    fontScale: Float,
    fontWeight: FontWeight = FontWeight.Normal,
    fontStyle: FontStyle = FontStyle.Normal,
    mono: Boolean = false,
) {
    Column(
        Modifier
            .fillMaxWidth()
            .background(container, RoundedCornerShape(14.dp))
            .padding(14.dp),
    ) {
        Text(
            text.trim(),
            color = onContainer,
            fontWeight = fontWeight,
                    fontSize = (if (mono) 14f else 15f * fontScale).sp,
                    lineHeight = (22f * fontScale).sp,
                )
    }
}

@Composable
private fun InlineRichText(
    text: String,
    entries: List<GlossaryEntry>,
    color: androidx.compose.ui.graphics.Color,
    accent: androidx.compose.ui.graphics.Color,
    fontSize: TextUnit,
    fontWeight: FontWeight,
    fontStyle: FontStyle = FontStyle.Normal,
) {
    val parts = remember(text) { splitParts(text) }
    val annotated = remember(parts, color, accent, fontSize, fontWeight, fontStyle) {
        buildAnnotatedString {
            val base = SpanStyle(color = color, fontSize = fontSize, fontWeight = fontWeight, fontStyle = fontStyle)
            val accentStyle = base.copy(color = accent, fontWeight = FontWeight.SemiBold)
            parts.forEach { part ->
                when (part) {
                    is RenderPart.Text -> withStyle(base) { append(part.value) }
                    is RenderPart.Term -> {
                        pushStringAnnotation(TERM_TAG, part.id)
                        withStyle(accentStyle) { append(part.label) }
                        pop()
                    }
                    is RenderPart.Link -> {
                        pushStringAnnotation(URL_TAG, part.url)
                        withStyle(accentStyle.copy(textDecoration = TextDecoration.Underline)) { append(part.label) }
                        pop()
                    }
                }
            }
        }
    }
    var selected by remember { mutableStateOf<GlossaryEntry?>(null) }
    ClickableText(
        text = annotated,
        style = MaterialTheme.typography.bodyLarge.copy(color = color, fontSize = fontSize),
        onClick = { offset ->
            annotated.getStringAnnotations(TERM_TAG, offset, offset).firstOrNull()?.item?.let { id ->
                entries.find { e ->
                    e.id.equals(id, true) || e.term.equals(id, true) ||
                        e.aliases.any { a -> a.equals(id, true) }
                }?.let { selected = it }
            }
            annotated.getStringAnnotations(URL_TAG, offset, offset).firstOrNull()?.item?.let { openUrl(it) }
        },
    )
    selected?.let { entry ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { selected = null },
            title = { Text(entry.term) },
            text = { Text(entry.naiveDefinition) },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { selected = null }) { Text("Закрыть") }
            },
        )
    }
}

private sealed interface MarkdownBlock {
    data class Heading(val text: String) : MarkdownBlock
    data class Subheading(val text: String) : MarkdownBlock
    data object Divider : MarkdownBlock
    data class Important(val text: String) : MarkdownBlock
    data class Template(val text: String) : MarkdownBlock
    data class Prompt(val text: String) : MarkdownBlock
    data class Bullet(val text: String) : MarkdownBlock
    data class Paragraph(val text: String, val bold: Boolean, val italic: Boolean) : MarkdownBlock
}

private fun parseBlocks(markdown: String): List<MarkdownBlock> {
    val result = mutableListOf<MarkdownBlock>()
    var i = 0
    val lines = markdown.lines()
    while (i < lines.size) {
        val line = lines[i].trim()
        when {
            line.startsWith(":::important") -> {
                i++
                val body = mutableListOf<String>()
                while (i < lines.size && lines[i].trim() != ":::") {
                    body += lines[i]
                    i++
                }
                result += MarkdownBlock.Important(body.joinToString("\n"))
                i++
            }
            line.startsWith(":::template") -> {
                i++
                val body = mutableListOf<String>()
                while (i < lines.size && lines[i].trim() != ":::") {
                    body += lines[i]
                    i++
                }
                result += MarkdownBlock.Template(body.joinToString("\n"))
                i++
            }
            line.startsWith(":::prompt") -> {
                i++
                val body = mutableListOf<String>()
                while (i < lines.size && lines[i].trim() != ":::") {
                    body += lines[i]
                    i++
                }
                result += MarkdownBlock.Prompt(body.joinToString("\n"))
                i++
            }
            line.startsWith("## ") -> {
                result += MarkdownBlock.Heading(line.removePrefix("## ").trim())
                i++
            }
            line.startsWith("### ") -> {
                result += MarkdownBlock.Subheading(line.removePrefix("### ").trim())
                i++
            }
            line == "---" -> {
                result += MarkdownBlock.Divider
                i++
            }
            line.startsWith("- ") -> {
                result += MarkdownBlock.Bullet(line.removePrefix("- ").trim())
                i++
            }
            line.startsWith("**") && line.endsWith("**") -> {
                result += MarkdownBlock.Paragraph(line.removeSurrounding("**"), bold = true, italic = false)
                i++
            }
            line.isNotBlank() -> {
                val bold = line.startsWith("**")
                val italic = line.startsWith("_") && line.endsWith("_")
                result += MarkdownBlock.Paragraph(line.trim(), bold, italic)
                i++
            }
            else -> i++
        }
    }
    return result
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
        result.add(RenderPart.Link(match.groupValues[1], match.groupValues[2]))
        last = match.range.last + 1
    }
    if (last < text.length) result.add(RenderPart.Text(text.substring(last)))
    return result
}
