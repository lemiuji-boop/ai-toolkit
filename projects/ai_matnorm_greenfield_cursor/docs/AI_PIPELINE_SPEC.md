# AI/OCR Pipeline Specification

## Pipeline

```text
Upload
  -> Normalize
  -> Classify
  -> Extract text layer
  -> Detect scan
  -> OCR if needed
  -> Layout analysis
  -> Table recognition
  -> Extract engineering facts
  -> Validate schemas
  -> Human review
  -> KSI
  -> Materials calculation
  -> Report/export
```

## Provider interfaces

```python
class LlmProvider:
    async def chat(self, request: LlmRequest) -> LlmResponse: ...

class OcrProvider:
    async def recognize(self, request: OcrRequest) -> OcrResult: ...

class LayoutProvider:
    async def analyze(self, request: LayoutRequest) -> LayoutResult: ...
```

## Model routing

Provider and model are selected by task type, not hardcoded in business logic.

Task types:

```text
DOCUMENT_CLASSIFICATION
OCR_CLEANUP
TITLE_BLOCK_EXTRACTION
SPEC_EXTRACTION
TECH_REQUIREMENTS_EXTRACTION
ASSEMBLY_LINKING
PROCESS_ANALYSIS
MATERIAL_EXPLANATION
REPORT_GENERATION
ASSISTANT_CHAT
```

## Required validation

Every AI response must be validated by Pydantic schema. Invalid response triggers retry with repair prompt or fallback provider.
