"""Mask endpoint - replace PII with asterisks in text or JSON."""

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
from app.services.masking import mask_text
from app.services.json_processor import mask_json


router = APIRouter(tags=["PII Masking"])


@router.post(
    "/mask",
    response_model=Union[MaskResponse, MaskJsonResponse],
    summary="🎭 Mask PII with asterisks (***)",
    description="""
**Replace detected PII entities with asterisks (`***`).**

This endpoint masks all detected PII by replacing it with `***`, regardless of the original length.

## Input Modes

### Text Mode
```json
{
  "text": "Contact John Doe at john@example.com"
}
```

**Result:** `"Contact *** at ***"`

### JSON Mode
```json
{
  "json": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  }
}
```

**Result:**
```json
{
  "user": {
    "name": "***",
    "email": "***",
    "age": 30
  }
}
```

## Example Response

```json
{
  "text": "Contact *** at ***",
  "entities": [
    {
      "type": "PERSON",
      "value": "John Doe",
      "start": 8,
      "end": 16,
      "masked_value": "***"
    },
    {
      "type": "EMAIL",
      "value": "john@example.com",
      "start": 20,
      "end": 36,
      "masked_value": "***"
    }
  ]
}
```

**Note:** JSON structure is preserved. Only string values are modified.
"""
)
async def mask_pii(request: UnifiedRequest) -> Union[MaskResponse, MaskJsonResponse]:
    """Mask PII entities in the provided text or JSON.
    
    Detects and replaces PII with asterisks:
    - Email addresses → ***
    - Phone numbers → ***
    - Credit card numbers → ***
    - Person names → ***
    
    For JSON input, only string values are processed.
    The JSON structure is preserved.
    """
    if request.is_json_mode:
        # JSON mode - mask in all string values
        masked_data, entities = mask_json(request.json, request.language)
        
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
        
        return MaskJsonResponse(json=masked_data, entities=json_entities)
    else:
        # Text mode - standard masking
        detector = get_detector()
        detected = detector.detect(request.text, request.language)
        
        masked_text, masked_entities = mask_text(request.text, detected)
        
        entities = [
            MaskedEntity(
                type=entity.type,
                value=entity.value,
                start=entity.start,
                end=entity.end,
                masked_value=entity.masked_value
            )
            for entity in masked_entities
        ]
        
        return MaskResponse(text=masked_text, entities=entities)
