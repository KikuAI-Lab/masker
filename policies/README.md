# Redaction Policies

YAML configuration files for PII redaction behavior.

## Default Policy

The `default.yaml` policy is used when no `policy_id` is specified.

## Policy Schema

```yaml
version: 1                    # Policy version

categories:                   # Action per PII type
  email: mask                 # Replace with ***
  phone: mask
  card: drop                  # Remove entirely
  person: placeholder         # Replace with <PERSON>

fail_mode: closed             # closed = block on error
                              # open = forward as-is on error
```

## Actions

| Action | Result |
|--------|--------|
| `mask` | `***` |
| `placeholder` | `<EMAIL>` |
| `hash` | `[a1b2c3d4]` |
| `drop` | (empty) |
| `keep` | (original) |

## Usage

```python
POST /v1/chat/completions
{
    "model": "gpt-4",
    "messages": [...],
    "policy_id": "strict"    # Uses policies/strict.yaml
}
```
