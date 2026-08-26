import html
from fastapi import HTTPException, status

DANGEROUS_PATTERNS = ["<script", "javascript:", "onload=", "onerror="]

def sanitize_input(text: str) -> str:
    """Escape HTML entities in input string."""
    if not text:
        return ""
    return html.escape(text.strip())

def validate_user_input(text: str | None, field_name: str = "Input", min_len: int = 1, max_len: int = 2000) -> str:
    """Validate text length and check for script injection patterns."""
    if text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is required."
        )

    stripped = text.strip()
    if len(stripped) < min_len:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be at least {min_len} character(s)."
        )

    if len(stripped) > max_len:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} exceeds maximum length of {max_len} characters."
        )

    lower_text = stripped.lower()
    for pattern in DANGEROUS_PATTERNS:
        if pattern in lower_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Potentially dangerous content detected in {field_name}."
            )

    return stripped
