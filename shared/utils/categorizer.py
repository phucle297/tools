"""Commit categorization by component"""

from typing import Literal

ComponentType = Literal["Console", "Server", "Others"]


def categorize_commit(message: str) -> ComponentType:
    message_lower = message.lower()

    console_keywords = [
        "console", "ui-block", "ui block", "frontend", "react", "detail",
        "icon", "style", "css", "component", "button", "modal", "dialog",
        "form", "layout", "page", "view", "screen", "ui", "ux",
    ]
    if any(keyword in message_lower for keyword in console_keywords):
        return "Console"

    server_keywords = [
        "server", "nest-core", "nestcore", "backend", "api", "endpoint",
        "controller", "service", "repository", "database", "db", "query",
        "migration",
    ]
    if any(keyword in message_lower for keyword in server_keywords):
        return "Server"

    return "Others"


def group_commits_by_component(commits: list[str]) -> dict[ComponentType, list[str]]:
    grouped: dict[ComponentType, list[str]] = {
        "Console": [],
        "Server": [],
        "Others": [],
    }

    for commit in commits:
        category = categorize_commit(commit)
        grouped[category].append(commit)

    return grouped
