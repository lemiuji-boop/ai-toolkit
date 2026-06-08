# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""NER и regex-извлечение полей; fallback без spaCy."""

import re
from functools import lru_cache

DOC_NUMBER_RE = re.compile(r"\b[А-ЯЁ]{4}\.\d{6}\.\d{3}\b")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


def _regex_extract(text: str) -> dict[str, dict[str, str | float]]:
    doc_number_match = DOC_NUMBER_RE.search(text)
    date_match = DATE_RE.search(text)
    return {
        "doc_number": {
            "value": doc_number_match.group(0) if doc_number_match else "",
            "confidence": 0.95 if doc_number_match else 0.0,
        },
        "release_date": {
            "value": date_match.group(0) if date_match else "",
            "confidence": 0.85 if date_match else 0.0,
        },
        "name": {"value": "", "confidence": 0.0},
    }


@lru_cache(maxsize=1)
def _get_nlp():
    import spacy

    return spacy.load("ru_core_news_lg")


def extract_fields(text: str) -> dict[str, dict[str, str | float]]:
    base = _regex_extract(text)
    try:
        nlp = _get_nlp()
        doc = nlp(text[:20000])
        names = [ent.text for ent in doc.ents if ent.label_ in {"PER", "ORG"}]
        if names and not base["name"]["value"]:
            base["name"] = {"value": names[0], "confidence": 0.7}
    except Exception:
        # spaCy модель недоступна — используем только regex
        pass
    return base
