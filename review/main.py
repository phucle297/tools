"""Review - Code review helper CLI"""

import typer
from typing import NamedTuple, Optional
from git import Repo, InvalidGitRepositoryError

app = typer.Typer(help="Review code changes efficiently", add_completion=True)


class FileReview(NamedTuple):
    """Information about a file review"""
    path: str
    status: str
    additions: int
    deletions: int
    changes: int


def get_staged_diff(repo: Repo) -> str:
    """Get staged diff"""
    return repo.git.diff("--cached")


def get_diff_as_string(repo: Repo, commit) -> str:
    """Get diff as string from a commit"""
    diff = commit.diff(commit.parents[0]) if commit.parents else commit.diff()
    if hasattr(diff, '__str__'):
        return str(diff)
    return diff or ""


def get_diff_stats(diff: str) -> dict[str, int]:
    """Extract statistics from diff"""
    stats = {"files": 0, "additions": 0, "deletions": 0}
    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            stats["files"] += 1
        elif line.startswith("+") and not line.startswith("+++"):
            stats["additions"] += 1
        elif line.startswith("-") and not line.startswith("---"):
            stats["deletions"] += 1
    stats["net_changes"] = stats["additions"] - stats["deletions"]
    return stats


def analyze_risky_files(diff: str) -> list[str]:
    """Identify potentially risky files"""
    risky = []
    for line in diff.split("\n"):
        if line.startswith("+++ b/"):
            path = line[6:]
            risky_patterns = [
                "migration", "schema", "database", "config", "secrets",
                ".env", "docker-compose", "deployment", "production"
            ]
            if any(p in path.lower() for p in risky_patterns):
                risky.append(path)
    return risky


def parse_diff_for_files(diff: str) -> list[FileReview]:
    """Parse diff to extract file information"""
    files = []
    current_file = ""
    additions = 0
    deletions = 0

    for line in diff.split("\n"):
        if line.startswith("+++ b/"):
            if current_file:
                status = "modified" if additions > 0 or deletions > 0 else "changed"
                files.append(FileReview(
                    path=current_file,
                    status=status,
                    additions=additions,
                    deletions=deletions,
                    changes=additions + deletions
                ))
            current_file = line[6:]
            additions = 0
            deletions = 0
        elif line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

    if current_file:
        status = "modified" if additions > 0 or deletions > 0 else "changed"
        files.append(FileReview(
            path=current_file,
            status=status,
            additions=additions,
            deletions=deletions,
            changes=additions + deletions
        ))

    return files


@app.command()
def diff(
    ai: bool = typer.Option(False, "--ai", "-a", help="Generate AI review summary"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full diff"),
):
    """Review staged changes"""
    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    staged_diff = get_staged_diff(repo)

    if not staged_diff:
        typer.echo("ℹ️  No staged changes")
        raise typer.Exit(code=0)

    stats = get_diff_stats(staged_diff)
    files = parse_diff_for_files(staged_diff)

    typer.echo("📋 Review Summary")
    typer.echo("-" * 40)
    typer.echo(f"Files: {stats['files']} | +{stats['additions']} | -{stats['deletions']} | {stats['net_changes']:+d}")

    risky = analyze_risky_files(staged_diff)
    if risky:
        typer.echo("\n⚠️  Potentially Risky Files:")
        for path in risky:
            typer.echo(f"  • {path}")

    typer.echo("\n📄 Files Changed:")
    for f in files:
        change = f"+{f.additions}" if f.additions > 0 else str(f.additions)
        change = f"-{f.deletions}" if f.deletions > 0 else change
        icon = "📝" if f.status == "modified" else "✨" if f.status == "added" else "🗑️"
        typer.echo(f"  {icon} {f.path} ({change})")

    if verbose:
        typer.echo("\n" + "=" * 60)
        typer.echo(staged_diff)

    if ai:
        typer.echo("\n🤖 AI Review Summary:")
        typer.echo("-" * 40)
        try:
            from shared.ai import AICommitSummarizer
            summarizer = AICommitSummarizer()
            summary = summarizer.summarize([staged_diff], "review")
            typer.echo(summary)
        except ValueError as e:
            typer.echo(f"⚠️  {e}")


@app.command()
def commit(
    hash: str = typer.Argument(..., help="Commit hash to review"),
    ai: bool = typer.Option(False, "--ai", "-a", help="Generate AI review summary"),
):
    """Review a specific commit"""
    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    try:
        commit = repo.commit(hash)
    except Exception:
        typer.echo(f"❌ Commit '{hash}' not found", err=True)
        raise typer.Exit(code=1)

    diff_str = get_diff_as_string(repo, commit)

    typer.echo(f"📋 Commit Review: {commit.hexsha[:7]}")
    typer.echo(f"Author: {commit.author.name}")
    typer.echo(f"Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M')}")
    typer.echo(f"\n{commit.message.strip()}")

    files = parse_diff_for_files(diff_str)
    stats = get_diff_stats(diff_str)

    typer.echo("\n" + "-" * 40)
    typer.echo(f"Files: {stats['files']} | +{stats['additions']} | -{stats['deletions']}")

    if ai:
        typer.echo("\n🤖 AI Review:")
        try:
            from shared.ai import AICommitSummarizer
            summarizer = AICommitSummarizer()
            summary = summarizer.summarize([commit.message], "review")
            typer.echo(summary)
        except ValueError as e:
            typer.echo(f"⚠️  {e}")


@app.command()
def stats(
    from_date: Optional[str] = typer.Option(None, "--from", "-f", help="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = typer.Option(None, "--to", "-t", help="End date (YYYY-MM-DD)"),
):
    """Show review statistics for a time period"""
    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    try:
        if from_date and to_date:
            from datetime import datetime
            since = datetime.strptime(from_date, "%Y-%m-%d")
            until = datetime.strptime(to_date, "%Y-%m-%d")
            commits = list(repo.iter_commits(since=since.isoformat(), until=until.isoformat()))
        else:
            commits = list(repo.iter_commits(no_merges=True))[:50]
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1)

    total_additions = 0
    total_deletions = 0
    total_files = 0

    typer.echo(f"📊 Review Stats (last {len(commits)} commits)")
    typer.echo("-" * 40)

    for c in commits[:10]:
        try:
            diff_str = get_diff_as_string(repo, c)
            stats = get_diff_stats(diff_str)
            total_additions += stats['additions']
            total_deletions += stats['deletions']
            total_files += stats['files']
        except Exception:
            pass

    typer.echo(f"Total files changed: {total_files}")
    typer.echo(f"Total additions: +{total_additions}")
    typer.echo(f"Total deletions: -{total_deletions}")
    typer.echo(f"Net changes: {total_additions - total_deletions:+d}")


def main():
    app(prog_name="review")


if __name__ == "__main__":
    main()
