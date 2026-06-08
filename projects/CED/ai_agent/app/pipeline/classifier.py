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

def classify_doc_type(text: str) -> dict[str, str | float]:
    text_l = text.lower()
    if "спецификац" in text_l:
        return {"doc_type": "specification", "confidence": 0.9}
    if "схем" in text_l:
        return {"doc_type": "scheme", "confidence": 0.82}
    if "черт" in text_l:
        return {"doc_type": "drawing", "confidence": 0.88}
    return {"doc_type": "other", "confidence": 0.5}
