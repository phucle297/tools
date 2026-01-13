"""Commit message generator - Git operations"""

from typing import NamedTuple, Optional

from git import Repo


class StagedFile(NamedTuple):
    """Information about a staged file"""

    path: str
    status: str


def get_staged_files(repo: Repo) -> list[StagedFile]:
    """Get list of staged files with their status"""
    staged: list[StagedFile] = []
    for item in repo.index.diff("HEAD"):
        status = "Modified"
        if item.new_file:
            status = "Added"
        elif item.deleted_file:
            status = "Deleted"
        elif item.renamed:
            status = "Renamed"
        path = item.a_path or ""
        if path:
            staged.append(StagedFile(path=path, status=status))
    return staged


def get_staged_diff(repo: Repo) -> str:
    """Get staged changes as a diff string"""
    return repo.git.diff("--cached")


def get_all_changes(repo: Repo) -> str:
    """Get all changes (staged + unstaged) as a diff string"""
    staged = repo.git.diff("--cached")
    unstaged = repo.git.diff()
    if staged and unstaged:
        return f"Staged:\n{staged}\n\nUnstaged:\n{unstaged}"
    return staged or unstaged


def analyze_diff_for_scope(diff: str) -> Optional[str]:
    """Analyze diff to suggest a scope based on changed files"""
    if not diff:
        return None

    files: list[str] = []
    for line in diff.split("\n"):
        if line.startswith("+++ b/") or line.startswith("a/"):
            raw_path = line[6:] if line.startswith("+++ b/") else line[2:]
            path = raw_path.strip()
            if path and not path.startswith(".git"):
                files.append(path)

    if not files:
        return None

    path_str = " ".join(files).lower()

    scope_indicators: dict[str, list[str]] = {
        "auth": ["auth", "login", "password", "token", "jwt"],
        "api": ["api", "endpoint", "route", "controller"],
        "db": ["db", "migration", "model", "schema", "query"],
        "ui": ["ui", "view", "page", "component", "button", "style", "css"],
        "test": ["test", "spec", "__tests__"],
        "docs": ["readme", "doc", ".md"],
    }

    for scope, keywords in scope_indicators.items():
        if any(kw in path_str for kw in keywords):
            return scope

    return None
