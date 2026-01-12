"""Advanced commands (filter, search, multirepo, tickets)"""

from collections import defaultdict

import typer

from report.cli.formatters import print_commits_table
from report.git.commits import (
    discover_repos_in_directory,
    get_commits_detailed,
    get_commits_from_multiple_repos,
)
from report.utils.dates import custom_range, last_n_days_range
from report.utils.tickets import group_commits_by_ticket

app = typer.Typer()


@app.command()
def filter(
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Filter commits from last N days",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter by author",
    ),
    exclude: str = typer.Option(
        None,
        "--exclude",
        "-x",
        help="Exclude commits matching pattern (comma-separated keywords)",
    ),
    include: str = typer.Option(
        None,
        "--include",
        "-i",
        help="Include only commits matching pattern (comma-separated keywords)",
    ),
    files: bool = typer.Option(
        False,
        "--files",
        "-f",
        help="Show files changed in each commit",
    ),
):
    """Filter commits with advanced options"""
    since, until = last_n_days_range(days)

    # Get commits
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo(f"No commits found in last {days} days.")
        raise typer.Exit(code=0)

    # Apply include filter
    if include:
        include_keywords = [k.strip().lower() for k in include.split(",")]
        commits_info = [
            c
            for c in commits_info
            if any(keyword in c.message.lower() for keyword in include_keywords)
        ]

    # Apply exclude filter
    if exclude:
        exclude_keywords = [k.strip().lower() for k in exclude.split(",")]
        commits_info = [
            c
            for c in commits_info
            if not any(keyword in c.message.lower() for keyword in exclude_keywords)
        ]

    if not commits_info:
        typer.echo("No commits match the filter criteria.")
        raise typer.Exit(code=0)

    title = f"📝 Filtered Commits - {len(commits_info)} match(es)"
    if author:
        title += f" (by {author})"

    typer.echo(f"\n{title}\n")
    print_commits_table(commits_info)

    # Show files if requested
    if files:
        from git import Repo

        repo = Repo(".", search_parent_directories=True)

        typer.echo("\n📁 Files Changed:\n")
        for commit in commits_info:
            try:
                git_commit = repo.commit(commit.hash)
                changed_files = list(git_commit.stats.files.keys())

                if changed_files:
                    typer.echo(f"  {commit.hash} - {commit.message[:50]}")
                    for file in changed_files[:5]:  # Show first 5 files
                        typer.echo(f"    • {file}")
                    if len(changed_files) > 5:
                        typer.echo(f"    ... and {len(changed_files) - 5} more")
                    typer.echo()
            except Exception as e:
                typer.echo(f"  {commit.hash} - Error: {e}")


@app.command()
def search(
    keyword: str = typer.Argument(
        ...,
        help="Keyword to search in commit messages",
    ),
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help="Search in last N days (default: 30)",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter by author",
    ),
    case_sensitive: bool = typer.Option(
        False,
        "--case-sensitive",
        "-c",
        help="Case-sensitive search",
    ),
):
    """Search commits by keyword"""
    since, until = last_n_days_range(days)

    # Get all commits
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo(f"No commits found in last {days} days.")
        raise typer.Exit(code=0)

    # Filter by keyword
    if case_sensitive:
        matching = [c for c in commits_info if keyword in c.message]
    else:
        keyword_lower = keyword.lower()
        matching = [c for c in commits_info if keyword_lower in c.message.lower()]

    # Display results
    if not matching:
        typer.echo(f"No commits found matching '{keyword}' in last {days} days.")
        raise typer.Exit(code=0)

    title = f"🔍 Search Results for '{keyword}'"
    if author:
        title += f" (by {author})"
    title += f" - {len(matching)} match(es)"

    typer.echo(f"\n{title}\n")
    print_commits_table(matching)


@app.command()
def multirepo(
    workspace: str = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace directory containing multiple repos",
    ),
    repos: str = typer.Option(
        None,
        "--repos",
        "-r",
        help="Comma-separated list of repository paths",
    ),
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Last N days (default: 7)",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author",
    ),
    discover: bool = typer.Option(
        False,
        "--discover",
        help="Auto-discover repositories in workspace",
    ),
):
    """Generate report across multiple repositories"""
    # Determine repository paths
    repo_paths = []

    if repos:
        repo_paths = [p.strip() for p in repos.split(",")]
    elif workspace:
        if discover:
            typer.echo(f"🔍 Discovering repositories in {workspace}...")
            repo_paths = discover_repos_in_directory(workspace)
            if not repo_paths:
                typer.echo(f"No repositories found in {workspace}")
                raise typer.Exit(code=1)
            typer.echo(f"Found {len(repo_paths)} repositories:\n")
            for rp in repo_paths:
                typer.echo(f"  • {rp}")
            typer.echo()
        else:
            # Use all subdirectories as potential repos
            import os

            try:
                repo_paths = [
                    os.path.join(workspace, d)
                    for d in os.listdir(workspace)
                    if os.path.isdir(os.path.join(workspace, d))
                ]
            except OSError as e:
                typer.echo(f"Error accessing workspace: {e}", err=True)
                raise typer.Exit(code=1)
    else:
        typer.echo("Error: Please specify --workspace or --repos", err=True)
        typer.echo("\nExamples:")
        typer.echo("  report multirepo --workspace ~/projects --discover")
        typer.echo("  report multirepo --repos /path/repo1,/path/repo2")
        raise typer.Exit(code=1)

    # Get date range
    since, until = last_n_days_range(days)

    # Get commits from all repos
    typer.echo(f"📊 Multi-Repository Report - last {days} days\n")

    commits_info = get_commits_from_multiple_repos(repo_paths, since, until, author)

    if not commits_info:
        typer.echo("No commits found across all repositories.")
        raise typer.Exit(code=0)

    # Group by repository
    by_repo = defaultdict(list)
    for commit in commits_info:
        by_repo[commit.repo].append(commit)

    typer.echo(f"Found {len(commits_info)} commit(s) across {len(by_repo)} repositories:\n")

    for repo_name in sorted(by_repo.keys()):
        repo_commits = by_repo[repo_name]
        typer.echo(f"📁 {repo_name} ({len(repo_commits)} commits)")
        print_commits_table(repo_commits, title=None)


@app.command()
def tickets(
    from_date: str = typer.Option(
        None,
        "--from",
        "-f",
        help="Start date (YYYY-MM-DD)",
    ),
    to_date: str = typer.Option(
        None,
        "--to",
        "-t",
        help="End date (YYYY-MM-DD)",
    ),
    days: int = typer.Option(
        7,
        "--days",
        "-d",
        help="Last N days (default: 7)",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author",
    ),
    patterns: str = typer.Option(
        None,
        "--patterns",
        "-p",
        help="Custom regex patterns for ticket extraction (comma-separated)",
    ),
):
    """Show commits grouped by ticket/issue numbers"""
    # Determine date range
    try:
        if from_date and to_date:
            since, until = custom_range(from_date, to_date)
            period_desc = f"{from_date} to {to_date}"
        else:
            since, until = last_n_days_range(days)
            period_desc = f"last {days} days"
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Get commits
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo(f"No commits found for period: {period_desc}")
        raise typer.Exit(code=0)

    # Parse custom patterns if provided
    custom_patterns = None
    if patterns:
        custom_patterns = [p.strip() for p in patterns.split(",")]

    # Group by ticket
    grouped, unmatched = group_commits_by_ticket(commits_info, custom_patterns)

    # Display results
    title = f"📋 Tickets Report - {period_desc}"
    if author:
        title += f" (by {author})"
    typer.echo(f"\n{title}\n")

    if grouped:
        typer.echo(
            f"Found {len(grouped)} ticket(s) with {sum(len(t.commits) for t in grouped)} commits:\n"
        )

        for ticket in grouped:
            typer.echo(f"🎫 {ticket.ticket_id} ({len(ticket.commits)} commits)")
            print_commits_table(ticket.commits, title=None)
    else:
        typer.echo("No tickets found in commits.")

    if unmatched:
        typer.echo(f"\n📝 {len(unmatched)} commit(s) without ticket numbers:")
        print_commits_table(unmatched, title=None)
