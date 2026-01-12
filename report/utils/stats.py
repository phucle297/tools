"""Git statistics and analytics"""

from datetime import datetime
from typing import NamedTuple

from git import InvalidGitRepositoryError, Repo


class AuthorStats(NamedTuple):
    """Statistics for a single author"""

    author: str
    total_commits: int
    files_changed: int
    insertions: int
    deletions: int
    net_lines: int


class RepoStats(NamedTuple):
    """Overall repository statistics"""

    total_commits: int
    total_authors: int
    total_files_changed: int
    total_insertions: int
    total_deletions: int
    net_lines: int
    author_stats: list[AuthorStats]


def get_commit_stats(
    repo_path: str,
    since: datetime,
    until: datetime,
    author: str | None = None,
) -> RepoStats:
    """Get detailed statistics for commits

    Args:
        repo_path: Path to git repository
        since: Start datetime for commit range
        until: End datetime for commit range
        author: Optional author filter

    Returns:
        RepoStats with detailed statistics
    """
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a git repository")

    commits = list(
        repo.iter_commits(
            since=since.isoformat(),
            until=until.isoformat(),
            no_merges=True,
            author=author if author and author.lower() != "me" else None,
        )
    )

    # Filter by "me" if needed
    if author and author.lower() == "me":
        try:
            git_user = repo.config_reader().get_value("user", "name")
            commits = [c for c in commits if c.author and c.author.name == git_user]
        except Exception:
            pass

    # Collect stats by author
    author_data: dict[str, dict] = {}
    all_files = set()

    for commit in commits:
        author_name = commit.author.name if commit.author and commit.author.name else "Unknown"

        if author_name not in author_data:
            author_data[author_name] = {
                "commits": 0,
                "files": set(),
                "insertions": 0,
                "deletions": 0,
            }

        author_data[author_name]["commits"] += 1

        # Get diff stats for this commit
        try:
            if commit.parents:
                diffs = commit.parents[0].diff(commit, create_patch=True)
                for diff in diffs:
                    # Track files changed
                    if diff.a_path:
                        author_data[author_name]["files"].add(diff.a_path)
                        all_files.add(diff.a_path)
                    if diff.b_path and diff.b_path != diff.a_path:
                        author_data[author_name]["files"].add(diff.b_path)
                        all_files.add(diff.b_path)

                    # Count lines changed
                    if diff.diff:
                        # Handle both bytes and str
                        if isinstance(diff.diff, bytes):
                            diff_text = diff.diff.decode("utf-8", errors="ignore")
                        else:
                            diff_text = diff.diff

                        for line in diff_text.split("\n"):
                            if line.startswith("+") and not line.startswith("+++"):
                                author_data[author_name]["insertions"] += 1
                            elif line.startswith("-") and not line.startswith("---"):
                                author_data[author_name]["deletions"] += 1
        except Exception:
            # Skip if can't get diff stats
            pass

    # Build author stats list
    author_stats_list = []
    total_insertions = 0
    total_deletions = 0

    for author_name, data in sorted(
        author_data.items(), key=lambda x: x[1]["commits"], reverse=True
    ):
        insertions = data["insertions"]
        deletions = data["deletions"]
        net = insertions - deletions

        total_insertions += insertions
        total_deletions += deletions

        author_stats_list.append(
            AuthorStats(
                author=author_name,
                total_commits=data["commits"],
                files_changed=len(data["files"]),
                insertions=insertions,
                deletions=deletions,
                net_lines=net,
            )
        )

    return RepoStats(
        total_commits=len(commits),
        total_authors=len(author_data),
        total_files_changed=len(all_files),
        total_insertions=total_insertions,
        total_deletions=total_deletions,
        net_lines=total_insertions - total_deletions,
        author_stats=author_stats_list,
    )
