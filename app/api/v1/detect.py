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
    summary="Detect PII in text or JSON",
    description="""
Scan text or JSON for PII entities without modifying content.

**Input modes:**
- `text`: Plain text string
- `json`: JSON object/array (processes string values recursively)

Returns detected entities with their types, values, and positions.
For JSON mode, includes the JSON path to each field.
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
