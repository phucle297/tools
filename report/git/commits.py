import os
from datetime import datetime
from typing import NamedTuple

from git import InvalidGitRepositoryError, Repo
from git.exc import GitError


class CommitInfo(NamedTuple):
    """Information about a single commit"""

    hash: str
    author: str
    date: str
    message: str
    repo: str = "."  # Repository name or path (with default)


def get_commits(
    repo_path: str,
    since: datetime,
    until: datetime,
    author: str | None = None,
) -> list[str]:
    """Get commit messages only (for backward compatibility)"""
    commits_info = get_commits_detailed(repo_path, since, until, author)
    return [c.message for c in commits_info]


def get_commits_detailed(
    repo_path: str,
    since: datetime,
    until: datetime,
    author: str | None = None,
) -> list[CommitInfo]:
    """Get detailed commit information

    Args:
        repo_path: Path to git repository
        since: Start datetime for commit range
        until: End datetime for commit range
        author: Optional author filter (supports "me" keyword for current git user)

    Returns:
        List of CommitInfo named tuples
    """
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a git repository")

    # Get all commits in the time range first
    all_commits = list(
        repo.iter_commits(
            since=since.isoformat(),
            until=until.isoformat(),
            no_merges=True,
        )
    )

    # Filter by author if specified
    if author:
        if author.lower() == "me":
            # Get current git user
            try:
                git_user = repo.config_reader().get_value("user", "name")
                all_commits = [c for c in all_commits if c.author and c.author.name == git_user]
            except Exception:
                pass  # If can't get git user, don't filter
        else:
            # Filter by specified author (case-insensitive)
            author_lower = author.lower()
            all_commits = [
                c
                for c in all_commits
                if c.author and c.author.name and author_lower in c.author.name.lower()
            ]

    commit_list: list[CommitInfo] = []
    for c in all_commits:
        raw = c.message
        if isinstance(raw, bytes):
            msg = raw.decode("utf-8", errors="ignore").strip()
        else:
            msg = raw.strip()

        if msg:
            commit_info = CommitInfo(
                hash=c.hexsha[:7],  # Short hash
                author=c.author.name if c.author and c.author.name else "Unknown",
                date=c.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                message=msg.split("\n")[0],  # First line only for table
            )
            commit_list.append(commit_info)

    return commit_list


def get_all_authors(
    repo_path: str,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[str]:
    """Get all unique authors in the repository

    Args:
        repo_path: Path to git repository
        since: Optional start datetime to filter authors
        until: Optional end datetime to filter authors

    Returns:
        List of unique author names sorted alphabetically
    """
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a git repository")

    # Build iterator with optional date filters
    if since and until:
        commits = repo.iter_commits(
            since=since.isoformat(),
            until=until.isoformat(),
            no_merges=True,
        )
    elif since:
        commits = repo.iter_commits(
            since=since.isoformat(),
            no_merges=True,
        )
    elif until:
        commits = repo.iter_commits(
            until=until.isoformat(),
            no_merges=True,
        )
    else:
        commits = repo.iter_commits(no_merges=True)

    authors = set()
    for c in commits:
        if c.author and c.author.name:
            authors.add(c.author.name)

    return sorted(list(authors))


def get_commits_from_multiple_repos(
    repo_paths: list[str],
    since: datetime,
    until: datetime,
    author: str | None = None,
) -> list[CommitInfo]:
    """Get commits from multiple repositories

    Args:
        repo_paths: List of repository paths
        since: Start datetime for commit range
        until: End datetime for commit range
        author: Optional author filter

    Returns:
        Combined list of CommitInfo from all repositories, sorted by date
    """
    all_commits: list[CommitInfo] = []

    for repo_path in repo_paths:
        try:
            commits = get_commits_detailed(repo_path, since, until, author)
            # Add repository name to each commit
            repo_name = os.path.basename(os.path.abspath(repo_path))
            commits_with_repo = [
                CommitInfo(
                    hash=c.hash,
                    author=c.author,
                    date=c.date,
                    message=c.message,
                    repo=repo_name,
                )
                for c in commits
            ]
            all_commits.extend(commits_with_repo)
        except (RuntimeError, InvalidGitRepositoryError, GitError, OSError) as e:
            # Skip invalid repos
            print(f"Warning: Skipping {repo_path}: {e}")
            continue

    # Sort by date (most recent first)
    all_commits.sort(key=lambda c: c.date, reverse=True)

    return all_commits


def discover_repos_in_directory(base_path: str, max_depth: int = 2) -> list[str]:
    """Discover git repositories in a directory

    Args:
        base_path: Base directory to search
        max_depth: Maximum depth to search (default: 2)

    Returns:
        List of repository paths
    """
    repos = []

    def _search(path: str, depth: int):
        if depth > max_depth:
            return

        try:
            # Check if current path is a git repo
            Repo(path)
            repos.append(path)
            return  # Don't search subdirectories of a repo
        except InvalidGitRepositoryError:
            pass

        # Search subdirectories
        try:
            for entry in os.listdir(path):
                subpath = os.path.join(path, entry)
                if os.path.isdir(subpath) and not entry.startswith("."):
                    _search(subpath, depth + 1)
        except (PermissionError, OSError):
            pass

    _search(base_path, 0)
    return repos
