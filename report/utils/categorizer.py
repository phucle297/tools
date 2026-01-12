"""Categorize commits by component"""

import re
from typing import Literal

ComponentType = Literal["Console", "Server", "Others"]


def categorize_commit(message: str) -> ComponentType:
    """
    Categorize a commit message into Console, Server, or Others

    Rules:
    - Contains "console", "ui-block", "detail", "icon", "style", etc. -> Console
    - Contains "server", "nest-core", etc. -> Server
    - Otherwise -> Others (will be further categorized by AI)
    """
    message_lower = message.lower()

    # Console keywords (UI/Frontend related)
    console_keywords = [
        "console",
        "ui-block",
        "ui block",
        "frontend",
        "react",
        "detail",
        "icon",
        "style",
        "css",
        "component",
        "button",
        "modal",
        "dialog",
        "form",
        "layout",
        "page",
        "view",
        "screen",
        "ui",
        "ux",
    ]
    if any(keyword in message_lower for keyword in console_keywords):
        return "Console"

    # Server keywords (Backend/API related)
    server_keywords = [
        "server",
        "nest-core",
        "nestcore",
        "backend",
        "api",
        "endpoint",
        "controller",
        "service",
        "repository",
        "database",
        "db",
        "query",
        "migration",
    ]
    if any(keyword in message_lower for keyword in server_keywords):
        return "Server"

    # Default to Others
    return "Others"


def group_commits_by_component(commits: list[str]) -> dict[ComponentType, list[str]]:
    """
    Group commits by component type

    Returns:
        Dict with keys: "Console", "Server", "Others"
    """
    grouped: dict[ComponentType, list[str]] = {
        "Console": [],
        "Server": [],
        "Others": [],
    }

    for commit in commits:
        category = categorize_commit(commit)
        grouped[category].append(commit)

    return grouped
