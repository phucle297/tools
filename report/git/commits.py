from datetime import datetime

from git import InvalidGitRepositoryError, Repo


def get_commits(
    repo_path: str,
    since: datetime,
    until: datetime,
) -> list[str]:
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not a git repository")

    commits = repo.iter_commits(
        since=since.isoformat(),
        until=until.isoformat(),
        no_merges=True,
    )

    messages: list[str] = []
    for c in commits:
        raw = c.message
        if isinstance(raw, bytes):
            msg = raw.decode("utf-8", errors="ignore").strip()
        else:
            msg = raw.strip()
        if msg:
            messages.append(msg)

    return messages
