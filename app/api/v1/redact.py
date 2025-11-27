"""Redact endpoint - replace PII with [REDACTED] in text or JSON."""

from typing import Union
from fastapi import APIRouter

from app.models.schemas import (
    UnifiedRequest,
    MaskResponse,
    MaskJsonResponse,
    MaskedEntity,
    JsonFieldEntity
)
from app.services.pii_detector import get_detector
from app.services.masking import redact_text
from app.services.json_processor import redact_json


router = APIRouter()


@router.post(
    "/redact",
    response_model=Union[MaskResponse, MaskJsonResponse],
    summary="🔒 Redact PII with [REDACTED]",
    description="""
**Replace detected PII entities with `[REDACTED]` placeholder.**

This endpoint **redacts** PII by replacing it with `[REDACTED]`. Use this when you want:
- Clear indication that content was redacted
- Consistent redaction pattern for all PII types
- Explicit privacy markers in your output

**Input modes:**
- **`text`**: Plain text string (max 32KB)
- **`json`**: JSON object/array (max 64KB total, redacts string values recursively, preserves structure)

**Example Request:**
```json
{
  "text": "Contact John Doe at john@example.com"
}
```

**Example Response:**
```json
{
  "text": "Contact [REDACTED] at [REDACTED]",
  "entities": [
    {"type": "PERSON", "value": "John Doe", "start": 8, "end": 16, "masked_value": "[REDACTED]"},
    {"type": "EMAIL", "value": "john@example.com", "start": 20, "end": 36, "masked_value": "[REDACTED]"}
  ]
}
```

**Note:** All PII types are redacted with the same placeholder (`[REDACTED]`).
"""
)
async def redact_pii(request: UnifiedRequest) -> Union[MaskResponse, MaskJsonResponse]:
    """Redact PII entities in the provided text or JSON.
    
    Detects and replaces PII with [REDACTED]:
    - Email addresses → [REDACTED]
    - Phone numbers → [REDACTED]
    - Credit card numbers → [REDACTED]
    - Person names → [REDACTED]
    
    For JSON input, only string values are processed.
    The JSON structure is preserved.
    """
    if request.is_json_mode:
        # JSON mode - redact in all string values
        redacted_data, entities = redact_json(request.json, request.language)
        
        json_entities = [
            JsonFieldEntity(
                path=e.path,
                type=e.type,
                value=e.value,
                start=e.start,
                end=e.end
            )
            for e in entities
        ]
        
        return MaskJsonResponse(json=redacted_data, entities=json_entities)
    else:
        # Text mode - standard redaction
        detector = get_detector()
        detected = detector.detect(request.text, request.language)
        
        redacted_text, redacted_entities = redact_text(request.text, detected)
        
        entities = [
            MaskedEntity(
                type=entity.type,
                value=entity.value,
                start=entity.start,
                end=entity.end,
                masked_value=entity.masked_value
            )
            for entity in redacted_entities
        ]
        
        return MaskResponse(text=redacted_text, entities=entities)
