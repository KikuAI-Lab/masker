"""JSON processing service for recursive PII detection and masking.

Handles recursive traversal of JSON structures, processing only
string values while preserving the original structure.
"""

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.services.masking import mask_text, redact_text
from app.services.pii_detector import get_detector


@dataclass
class JsonFieldEntity:
    """Entity found within a JSON field."""

    path: str
    type: str
    value: str
    start: int
    end: int


@dataclass
class JsonMaskedEntity(JsonFieldEntity):
    """Entity with masking information."""

    masked_value: str


def _build_path(current_path: str, key: Any) -> str:
    """Build JSON path string.

    Args:
        current_path: Current path prefix
        key: Key or index to append

    Returns:
        Updated path string (e.g., "user.name" or "items[0]")
    """
    if isinstance(key, int):
        return f"{current_path}[{key}]" if current_path else f"[{key}]"
    else:
        return f"{current_path}.{key}" if current_path else str(key)


def process_json_recursive(
    data: Any,
    processor: Callable[[str], tuple[str, list]],
    path: str = ""
) -> tuple[Any, list[JsonFieldEntity]]:
    """Recursively process JSON, applying processor to string values.

    Args:
        data: JSON data (dict, list, or primitive)
        processor: Function that takes a string and returns (processed_string, entities)
        path: Current JSON path for entity tracking

    Returns:
        Tuple of (processed_data, list of entities with paths)
    """
    all_entities = []

    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            new_path = _build_path(path, key)
            processed_value, entities = process_json_recursive(value, processor, new_path)
            result[key] = processed_value
            all_entities.extend(entities)
        return result, all_entities

    elif isinstance(data, list):
        result = []
        for idx, item in enumerate(data):
            new_path = _build_path(path, idx)
            processed_item, entities = process_json_recursive(item, processor, new_path)
            result.append(processed_item)
            all_entities.extend(entities)
        return result, all_entities

    elif isinstance(data, str):
        processed_str, raw_entities = processor(data)
        # Convert raw entities to JsonFieldEntity with path
        entities_with_path = [
            JsonFieldEntity(
                path=path,
                type=e.type if hasattr(e, 'type') else e.entity_type,
                value=e.value if hasattr(e, 'value') else "",
                start=e.start,
                end=e.end
            )
            for e in raw_entities
        ]
        return processed_str, entities_with_path

    else:
        # Numbers, booleans, None - return unchanged
        return data, []


def detect_json(
    data: Any,
    language: str = "en",
    entity_types: list[str] | None = None
) -> tuple[Any, list[JsonFieldEntity]]:
    """Detect PII in JSON structure without modifying it.

    Args:
        data: JSON data to scan
        language: Language for NER
        entity_types: Optional list of entity types to detect

    Returns:
        Tuple of (original_data, list of detected entities with paths)
    """
    detector = get_detector()

    def detect_processor(text: str) -> tuple[str, list]:
        entities = detector.detect(text, language, entity_types)
        return text, entities  # Return original text unchanged

    _, entities = process_json_recursive(data, detect_processor)
    return data, entities


def mask_json(
    data: Any,
    language: str = "en",
    entity_types: list[str] | None = None
) -> tuple[Any, list[JsonFieldEntity]]:
    """Mask PII in JSON structure with ***.

    Args:
        data: JSON data to process
        language: Language for NER
        entity_types: Optional list of entity types to mask

    Returns:
        Tuple of (masked_data, list of detected entities with paths)
    """
    detector = get_detector()

    def mask_processor(text: str) -> tuple[str, list]:
        entities = detector.detect(text, language, entity_types)
        masked_text, masked_entities = mask_text(text, entities)
        return masked_text, entities  # Return original entities for reporting

    return process_json_recursive(copy.deepcopy(data), mask_processor)


def redact_json(
    data: Any,
    language: str = "en",
    entity_types: list[str] | None = None
) -> tuple[Any, list[JsonFieldEntity]]:
    """Redact PII in JSON structure with [REDACTED].

    Args:
        data: JSON data to process
        language: Language for NER
        entity_types: Optional list of entity types to redact

    Returns:
        Tuple of (redacted_data, list of detected entities with paths)
    """
    detector = get_detector()

    def redact_processor(text: str) -> tuple[str, list]:
        entities = detector.detect(text, language, entity_types)
        redacted_text, _ = redact_text(text, entities)
        return redacted_text, entities

    return process_json_recursive(copy.deepcopy(data), redact_processor)


def process_json_with_mode(
    data: Any,
    language: str = "en",
    mode: str = "mask",
    entities_filter: list[str] | None = None
) -> tuple[Any, list[JsonFieldEntity]]:
    """Process JSON with specified mode and optional entity filtering.

    Args:
        data: JSON data to process
        language: Language for NER
        mode: "mask" for ***, "placeholder" for <TYPE>
        entities_filter: List of entity types to process (None = all)

    Returns:
        Tuple of (processed_data, list of detected entities with paths)
    """
    from app.services.redaction import (
        MASK_TOKEN,
        PLACEHOLDER_TEMPLATES,
        filter_entities,
    )

    detector = get_detector()

    def custom_processor(text: str) -> tuple[str, list]:
        # Detect entities
        detected = detector.detect(text, language)

        # Filter if needed
        if entities_filter:
            detected = filter_entities(detected, entities_filter)

        if not detected:
            return text, []

        # Apply appropriate replacement based on mode
        if mode == "placeholder":
            # Sort by start descending for right-to-left replacement
            sorted_entities = sorted(detected, key=lambda e: e.start, reverse=True)
            result = text
            for entity in sorted_entities:
                replacement = PLACEHOLDER_TEMPLATES.get(entity.type, f"<{entity.type}>")
                result = result[:entity.start] + replacement + result[entity.end:]
            return result, detected
        else:
            # mask mode
            sorted_entities = sorted(detected, key=lambda e: e.start, reverse=True)
            result = text
            for entity in sorted_entities:
                result = result[:entity.start] + MASK_TOKEN + result[entity.end:]
            return result, detected

    return process_json_recursive(copy.deepcopy(data), custom_processor)

