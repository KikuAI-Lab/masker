"""Text masking and redaction service.

Provides functions to replace detected PII entities with
mask tokens or redaction placeholders.
"""

from dataclasses import dataclass
from typing import Sequence

from app.core.config import settings
from app.services.pii_detector import DetectedEntity


@dataclass
class MaskedEntity:
    """Entity with masking information."""
    
    type: str
    value: str
    start: int
    end: int
    masked_value: str


def apply_replacements(
    text: str,
    entities: Sequence[DetectedEntity],
    replacement: str
) -> tuple[str, list[MaskedEntity]]:
    """Replace detected entities with the specified replacement string.
    
    Entities are replaced from right to left to preserve correct
    positions during replacement.
    
    Args:
        text: Original text
        entities: List of detected entities to replace
        replacement: String to use as replacement
        
    Returns:
        Tuple of (masked_text, list of MaskedEntity with original info)
    """
    if not entities:
        return text, []
    
    # Sort entities by start position descending (right to left)
    sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
    
    result = text
    masked_entities = []
    
    for entity in sorted_entities:
        # Replace the entity in the text
        result = result[:entity.start] + replacement + result[entity.end:]
        
        # Record the masked entity (with original positions)
        masked_entities.append(MaskedEntity(
            type=entity.type,
            value=entity.value,
            start=entity.start,
            end=entity.end,
            masked_value=replacement
        ))
    
    # Reverse to get entities in original order (by start position)
    masked_entities.reverse()
    
    return result, masked_entities


def mask_text(
    text: str,
    entities: Sequence[DetectedEntity]
) -> tuple[str, list[MaskedEntity]]:
    """Mask detected entities with asterisks.
    
    Args:
        text: Original text
        entities: List of detected entities
        
    Returns:
        Tuple of (masked_text, list of MaskedEntity)
    """
    return apply_replacements(text, entities, settings.mask_token)


def redact_text(
    text: str,
    entities: Sequence[DetectedEntity]
) -> tuple[str, list[MaskedEntity]]:
    """Redact detected entities with [REDACTED] placeholder.
    
    Args:
        text: Original text
        entities: List of detected entities
        
    Returns:
        Tuple of (redacted_text, list of MaskedEntity)
    """
    return apply_replacements(text, entities, settings.redact_token)

