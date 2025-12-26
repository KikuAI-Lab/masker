"""Text masking and redaction service.

Provides functions to replace detected PII entities with
mask tokens or redaction placeholders.
"""

from collections.abc import Sequence
from dataclasses import dataclass

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
    text: str, entities: Sequence[DetectedEntity], replacement: str
) -> tuple[str, list[MaskedEntity]]:
    """Replace detected entities with the specified replacement string.

    Entities are replaced from left to right to build the result string efficiently.

    Args:
        text: Original text
        entities: List of detected entities to replace
        replacement: String to use as replacement

    Returns:
        Tuple of (masked_text, list of MaskedEntity with original info)
    """
    if not entities:
        return text, []

    # Sort entities by start position (left to right)
    sorted_entities = sorted(entities, key=lambda e: e.start)

    result_parts = []
    masked_entities = []
    last_end = 0

    for entity in sorted_entities:
        # Append text before the entity
        result_parts.append(text[last_end : entity.start])
        # Append replacement
        result_parts.append(replacement)

        # Record the masked entity (with original positions)
        masked_entities.append(
            MaskedEntity(
                type=entity.type,
                value=entity.value,
                start=entity.start,
                end=entity.end,
                masked_value=replacement,
            )
        )

        last_end = entity.end

    # Append remaining text
    result_parts.append(text[last_end:])

    return "".join(result_parts), masked_entities


def mask_text(text: str, entities: Sequence[DetectedEntity]) -> tuple[str, list[MaskedEntity]]:
    """Mask detected entities with asterisks.

    Args:
        text: Original text
        entities: List of detected entities

    Returns:
        Tuple of (masked_text, list of MaskedEntity)
    """
    return apply_replacements(text, entities, settings.mask_token)


def redact_text(text: str, entities: Sequence[DetectedEntity]) -> tuple[str, list[MaskedEntity]]:
    """Redact detected entities with [REDACTED] placeholder.

    Args:
        text: Original text
        entities: List of detected entities

    Returns:
        Tuple of (redacted_text, list of MaskedEntity)
    """
    return apply_replacements(text, entities, settings.redact_token)
