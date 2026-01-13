"""Commit message generator - Utilities"""

from typing import Optional


CONVENTIONAL_TYPES = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "build",
    "ci",
    "chore",
    "revert",
]


def generate_conventional_message(
    commit_type: str,
    scope: Optional[str],
    subject: str,
    body: Optional[str] = None,
) -> str:
    """Generate a conventional commit message"""
    if scope:
        return f"{commit_type}({scope}): {subject}"
    return f"{commit_type}: {subject}"


def validate_subject(subject: str) -> tuple[bool, str]:
    """Validate commit subject"""
    if not subject:
        return False, "Subject is required"

    if len(subject) > 50:
        return False, "Subject too long (max 50 characters)"

    if subject[0].isupper():
        return False, "Subject should not start with capital letter"

    if subject.endswith("."):
        return False, "Subject should not end with period"

    return True, ""
