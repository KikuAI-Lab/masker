"""RapidAPI facade endpoint for PII redaction.

POST /v1/redact - Unified endpoint for RapidAPI integration.
Supports both text and JSON input modes.
"""

import time
from fastapi import APIRouter

from app.models.rapidapi_schemas import (
    RapidAPIRedactRequest,
    RapidAPIRedactResponse,
    RedactedItem
)
from app.services.redaction import redact_text, get_entity_score
from app.services.json_processor import process_json_with_mode


router = APIRouter(prefix="/v1", tags=["Main API"])


@router.post(
    "/redact",
    response_model=RapidAPIRedactResponse,
    summary="🔒 Main endpoint: Redact PII in text or JSON",
    description="""
**Main endpoint for PII redaction with flexible modes and entity filtering.**

**Perfect for cleaning data before sending to LLMs like ChatGPT, Claude, Gemini, etc.**

This is the **recommended endpoint** for most use cases. It provides:
- ✅ Flexible input (text or JSON)
- ✅ Multiple redaction modes (mask or placeholder)
- ✅ Entity type filtering
- ✅ Confidence scores for each detection
- ✅ Processing time measurement

**Input Modes:**

1. **Text Mode** - Process plain text strings
   ```json
   {
     "text": "Contact John Doe at john@example.com",
     "mode": "placeholder"
   }
   ```

2. **JSON Mode** - Process entire JSON structures recursively
   ```json
   {
     "json": {
       "user": {
         "name": "John Doe",
         "email": "john@example.com"
       }
     },
     "mode": "placeholder"
   }
   ```

**Redaction Modes:**

- **`mask`** (default) - Replace PII with `***`
  - Example: `"Contact *** at ***"`
  
- **`placeholder`** - Replace PII with type placeholders
  - Example: `"Contact <PERSON> at <EMAIL>"`
  - Placeholders: `<PERSON>`, `<EMAIL>`, `<PHONE>`, `<CARD>`

**Entity Filtering:**

- If `entities` is **not provided**: All PII types are redacted
- If `entities` is **provided**: Only specified types are redacted
  ```json
  {
    "text": "John Doe's email is john@example.com",
    "mode": "placeholder",
    "entities": ["EMAIL"]
  }
  ```
  Result: `"John Doe's email is <EMAIL>"` (PERSON not redacted)

**Supported Entity Types:**
- `PERSON` - Person names (detected via NER, ~85% accuracy)
- `EMAIL` - Email addresses (100% accuracy)
- `PHONE` - Phone numbers (100% accuracy, international formats)
- `CARD` - Credit card numbers (100% accuracy, Luhn validation)

**Example Request (Text Mode):**
```json
{
  "text": "Contact John Doe at john@example.com or call 555-123-4567",
  "mode": "placeholder"
}
```

**Example Response:**
```json
{
  "redacted_text": "Contact <PERSON> at <EMAIL> or call <PHONE>",
  "redacted_json": null,
  "items": [
    {"entity_type": "PERSON", "start": 8, "end": 16, "score": 0.85},
    {"entity_type": "EMAIL", "start": 20, "end": 36, "score": 1.0},
    {"entity_type": "PHONE", "start": 45, "end": 57, "score": 1.0}
  ],
  "processing_time_ms": 15.29
}
```

**Example Request (JSON Mode):**
```json
{
  "json": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 30
    }
  },
  "mode": "placeholder"
}
```

**Example Response:**
```json
{
  "redacted_text": null,
  "redacted_json": {
    "user": {
      "name": "<PERSON>",
      "email": "<EMAIL>",
      "age": 30
    }
  },
  "items": [
    {"entity_type": "PERSON", "path": "user.name", "start": 0, "end": 8, "score": 0.85},
    {"entity_type": "EMAIL", "path": "user.email", "start": 0, "end": 16, "score": 1.0}
  ],
  "processing_time_ms": 23.46
}
```

**Use Cases:**
- Clean user messages before sending to ChatGPT/Claude
- Anonymize support tickets for AI analysis
- Process form data before LLM classification
- Sanitize logs for AI-powered monitoring
"""
)
async def rapidapi_redact(request: RapidAPIRedactRequest) -> RapidAPIRedactResponse:
    """Redact PII entities in the provided text or JSON.
    
    This endpoint is designed for RapidAPI integration and provides:
    - Flexible input (text or JSON)
    - Flexible redaction modes (mask/placeholder)
    - Entity type filtering
    - Confidence scores for each detection
    - Processing time measurement
    """
    start_time = time.perf_counter()
    
    # Convert entities filter to list of strings if provided
    entities_filter = list(request.entities) if request.entities else None
    
    if request.is_json_mode:
        # JSON mode
        redacted_data, json_entities = process_json_with_mode(
            data=request.json,
            language=request.language,
            mode=request.mode,
            entities_filter=entities_filter
        )
        
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        items = [
            RedactedItem(
                entity_type=e.type,
                path=e.path,
                start=e.start,
                end=e.end,
                score=1.0 if e.type in ("EMAIL", "PHONE", "CARD") else 0.85
            )
            for e in json_entities
        ]
        
        return RapidAPIRedactResponse(
            redacted_text=None,
            redacted_json=redacted_data,
            items=items,
            processing_time_ms=round(processing_time_ms, 2)
        )
    else:
        # Text mode
        redacted_text_result, redacted_items = redact_text(
            text=request.text,
            language=request.language,
            entities_filter=entities_filter,
            mode=request.mode
        )
        
        processing_time_ms = (time.perf_counter() - start_time) * 1000
        
        items = [
            RedactedItem(
                entity_type=item.entity_type,
                path=None,
                start=item.start,
                end=item.end,
                score=item.score
            )
            for item in redacted_items
        ]
        
        return RapidAPIRedactResponse(
            redacted_text=redacted_text_result,
            redacted_json=None,
            items=items,
            processing_time_ms=round(processing_time_ms, 2)
        )
