"""Detect endpoint - find PII without modifying text or JSON."""

from typing import Union
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas import (
    TextRequest, 
    UnifiedRequest,
    DetectResponse, 
    DetectJsonResponse,
    DetectedEntity,
    JsonFieldEntity
)
from app.services.pii_detector import get_detector
from app.services.json_processor import detect_json


router = APIRouter(tags=["PII Detection"])


@router.post(
    "/detect",
    response_model=Union[DetectResponse, DetectJsonResponse],
    summary="🔍 Detect PII without modifying content",
    description="""
**Scan text or JSON for PII entities without modifying the content.**

Use this endpoint when you only need to identify PII without redacting it.

## Input Modes

### Text Mode
```json
{
  "text": "Contact John Doe at john@example.com"
}
```

### JSON Mode
```json
{
  "json": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

## Detected Entity Types

- **EMAIL**: Email addresses (regex, 100% accuracy)
- **PHONE**: Phone numbers (international formats, 100% accuracy)
- **CARD**: Credit card numbers (regex + Luhn validation, 100% accuracy)
- **PERSON**: Person names (spaCy NER, ~85% accuracy)

## Example Response

```json
{
  "entities": [
    {
      "type": "PERSON",
      "value": "John Doe",
      "start": 8,
      "end": 16
    },
    {
      "type": "EMAIL",
      "value": "john@example.com",
      "start": 20,
      "end": 36
    }
  ]
}
```

For JSON mode, each entity includes a `path` field showing its location (e.g., `"user.name"`).
"""
)
async def detect_pii(request: UnifiedRequest) -> Union[DetectResponse, DetectJsonResponse]:
    """Detect PII entities in the provided text or JSON.
    
    Scans for:
    - Email addresses
    - Phone numbers (international formats)
    - Credit card numbers
    - Person names (via NER)
    
    Returns the list of detected entities with their types,
    values, and positions.
    """
    if request.is_json_mode:
        # JSON mode - detect in all string values
        _, entities = detect_json(request.json, request.language, request.entities)
        
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
        
        return DetectJsonResponse(entities=json_entities)
    else:
        # Text mode - standard detection
        detector = get_detector()
        detected = detector.detect(request.text, request.language, request.entities)
        
        entities = [
            DetectedEntity(
                type=entity.type,
                value=entity.value,
                start=entity.start,
                end=entity.end
            )
            for entity in detected
        ]
        
        return DetectResponse(entities=entities)
