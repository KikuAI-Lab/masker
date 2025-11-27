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


router = APIRouter()


@router.post(
    "/detect",
    response_model=Union[DetectResponse, DetectJsonResponse],
    summary="🔍 Detect PII without modifying content",
    description="""
**Scan text or JSON for PII entities without modifying the original content.**

This endpoint only **detects** PII - it doesn't modify your data. Use this when you want to:
- Check if content contains PII before processing
- Get a list of detected entities with their positions
- Analyze PII distribution in your data

**Input modes:**
- **`text`**: Plain text string (max 32KB)
- **`json`**: JSON object/array (max 64KB total, processes string values recursively)

**Returns:**
- List of detected entities with types, values, and positions
- For JSON mode: includes JSON path to each field (e.g., `"user.email"`)

**Example Request (Text):**
```json
{
  "text": "Contact John Doe at john@example.com or call 555-123-4567"
}
```

**Example Response:**
```json
{
  "entities": [
    {"type": "PERSON", "value": "John Doe", "start": 8, "end": 16},
    {"type": "EMAIL", "value": "john@example.com", "start": 20, "end": 36},
    {"type": "PHONE", "value": "555-123-4567", "start": 45, "end": 57}
  ]
}
```
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
        _, entities = detect_json(request.json, request.language)
        
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
        detected = detector.detect(request.text, request.language)
        
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
