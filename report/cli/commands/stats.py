"""Statistics and comparison commands"""

from datetime import date as date_module

import typer

from report.utils.dates import (
    custom_range,
    last_n_days_range,
    last_week_range,
    month_range,
    this_week_range,
    today_range,
    yesterday_range,
)
from report.utils.stats import get_commit_stats

app = typer.Typer()


@app.command()
def stats(
    period: str = typer.Argument(
        "daily",
        help="Time period: daily, yesterday, weekly, lastweek, or use with range options",
    ),
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
        None,
        "--days",
        "-d",
        help="Last N days (including today)",
    ),
    month: int = typer.Option(
        None,
        "--month",
        "-m",
        help="Month number (1-12, uses current year)",
    ),
    year: int = typer.Option(
        None,
        "--year",
        "-y",
        help="Year (used with --month)",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter stats by author (use 'me' for current git user)",
    ),
):
    """Show git statistics and analytics"""
    # Determine date range
    try:
        if from_date and to_date:
            since, until = custom_range(from_date, to_date)
            period_desc = f"{from_date} to {to_date}"
        elif days:
            since, until = last_n_days_range(days)
            period_desc = f"last {days} days"
        elif month:
            if year:
                since, until = month_range(year, month)
                period_desc = f"{year}-{month:02d}"
            else:
                current_year = date_module.today().year
                since, until = month_range(current_year, month)
                period_desc = f"{current_year}-{month:02d}"
        else:
            # Use named period
            if period == "daily" or period == "today":
                since, until = today_range()
                period_desc = "today"
            elif period == "yesterday":
                since, until = yesterday_range()
                period_desc = "yesterday"
            elif period == "weekly" or period == "week":
                since, until = this_week_range()
                period_desc = "this week"
            elif period == "lastweek":
                since, until = last_week_range()
                period_desc = "last week"
            else:
                typer.echo(f"Error: Unknown period '{period}'", err=True)
                typer.echo("\nValid periods: daily, yesterday, weekly, lastweek")
                typer.echo("Or use custom range: --from/--to, --days, or --month")
                raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Get statistics
    try:
        repo_stats = get_commit_stats(".", since, until, author)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Display stats
    title = f"📊 Git Statistics - {period_desc}"
    if author:
        title += f" (by {author})"
    typer.echo(f"\n{title}\n")
    typer.echo("=" * 60)

    # Overall stats
    typer.echo(f"\n📈 Overview:")
    typer.echo(f"  Total Commits:       {repo_stats.total_commits}")
    typer.echo(f"  Total Contributors:  {repo_stats.total_authors}")
    typer.echo(f"  Files Changed:       {repo_stats.total_files_changed}")
    typer.echo(f"  Lines Added:         +{repo_stats.total_insertions}")
    typer.echo(f"  Lines Deleted:       -{repo_stats.total_deletions}")
    net_sign = "+" if repo_stats.net_lines >= 0 else ""
    typer.echo(f"  Net Lines:           {net_sign}{repo_stats.net_lines}")

    # Per-author stats
    if repo_stats.author_stats:
        typer.echo(f"\n👤 Per-Author Statistics:\n")

        # Header
        typer.echo(
            "┌─"
            + "─" * 20
            + "─┬─"
            + "─" * 8
            + "─┬─"
            + "─" * 8
            + "─┬─"
            + "─" * 10
            + "─┬─"
            + "─" * 10
            + "─┬─"
            + "─" * 10
            + "─┐"
        )
        typer.echo(
            "│ "
            + "Author".ljust(20)
            + " │ "
            + "Commits".ljust(8)
            + " │ "
            + "Files".ljust(8)
            + " │ "
            + "Added".ljust(10)
            + " │ "
            + "Deleted".ljust(10)
            + " │ "
            + "Net".ljust(10)
            + " │"
        )
        typer.echo(
            "├─"
            + "─" * 20
            + "─┼─"
            + "─" * 8
            + "─┼─"
            + "─" * 8
            + "─┼─"
            + "─" * 10
            + "─┼─"
            + "─" * 10
            + "─┼─"
            + "─" * 10
            + "─┤"
        )

        # Rows
        for author_stat in repo_stats.author_stats:
            author_name = author_stat.author[:20]  # Truncate if too long
            net_sign = "+" if author_stat.net_lines >= 0 else ""

            typer.echo(
                "│ "
                + author_name.ljust(20)
                + " │ "
                + str(author_stat.total_commits).ljust(8)
                + " │ "
                + str(author_stat.files_changed).ljust(8)
                + " │ "
                + f"+{author_stat.insertions}".ljust(10)
                + " │ "
                + f"-{author_stat.deletions}".ljust(10)
                + " │ "
                + f"{net_sign}{author_stat.net_lines}".ljust(10)
                + " │"
            )

        # Footer
        typer.echo(
            "└─"
            + "─" * 20
            + "─┴─"
            + "─" * 8
            + "─┴─"
            + "─" * 8
            + "─┴─"
            + "─" * 10
            + "─┴─"
            + "─" * 10
            + "─┴─"
            + "─" * 10
            + "─┘"
        )

    typer.echo()


@app.command()
def compare(
    period1: str = typer.Argument(
        ...,
        help="First period: thisweek, lastweek, or use with --from1/--to1",
    ),
    period2: str = typer.Argument(
        ...,
        help="Second period: thisweek, lastweek, or use with --from2/--to2",
    ),
    from1: str = typer.Option(
        None,
        "--from1",
        help="Start date for period 1 (YYYY-MM-DD)",
    ),
    to1: str = typer.Option(
        None,
        "--to1",
        help="End date for period 1 (YYYY-MM-DD)",
    ),
    from2: str = typer.Option(
        None,
        "--from2",
        help="Start date for period 2 (YYYY-MM-DD)",
    ),
    to2: str = typer.Option(
        None,
        "--to2",
        help="End date for period 2 (YYYY-MM-DD)",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter by author",
    ),
):
    """Compare git statistics between two time periods"""
    # Parse period 1
    try:
        if from1 and to1:
            since1, until1 = custom_range(from1, to1)
            period1_desc = f"{from1} to {to1}"
        elif period1 == "thisweek" or period1 == "week":
            since1, until1 = this_week_range()
            period1_desc = "this week"
        elif period1 == "lastweek":
            since1, until1 = last_week_range()
            period1_desc = "last week"
        elif period1 == "today":
            since1, until1 = today_range()
            period1_desc = "today"
        elif period1 == "yesterday":
            since1, until1 = yesterday_range()
            period1_desc = "yesterday"
        else:
            typer.echo(f"Error: Unknown period '{period1}'", err=True)
            raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Error in period 1: {e}", err=True)
        raise typer.Exit(code=1)

    # Parse period 2
    try:
        if from2 and to2:
            since2, until2 = custom_range(from2, to2)
            period2_desc = f"{from2} to {to2}"
        elif period2 == "thisweek" or period2 == "week":
            since2, until2 = this_week_range()
            period2_desc = "this week"
        elif period2 == "lastweek":
            since2, until2 = last_week_range()
            period2_desc = "last week"
        elif period2 == "today":
            since2, until2 = today_range()
            period2_desc = "today"
        elif period2 == "yesterday":
            since2, until2 = yesterday_range()
            period2_desc = "yesterday"
        else:
            typer.echo(f"Error: Unknown period '{period2}'", err=True)
            raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Error in period 2: {e}", err=True)
        raise typer.Exit(code=1)

    # Get stats for both periods
    try:
        stats1 = get_commit_stats(".", since1, until1, author)
        stats2 = get_commit_stats(".", since2, until2, author)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Display comparison
    title = f"📊 Comparison: {period1_desc} vs {period2_desc}"
    if author:
        title += f" (by {author})"
    typer.echo(f"\n{title}\n")
    typer.echo("=" * 70)

    # Side-by-side comparison
    typer.echo(f"\n{'Metric':<30} {period1_desc:<20} {period2_desc:<20} Δ")
    typer.echo("-" * 70)

    # Commits
    commits_diff = stats2.total_commits - stats1.total_commits
    commits_sign = "+" if commits_diff > 0 else ""
    typer.echo(
        f"{'Total Commits':<30} {stats1.total_commits:<20} {stats2.total_commits:<20} {commits_sign}{commits_diff}"
    )

    # Authors
    authors_diff = stats2.total_authors - stats1.total_authors
    authors_sign = "+" if authors_diff > 0 else ""
    typer.echo(
        f"{'Contributors':<30} {stats1.total_authors:<20} {stats2.total_authors:<20} {authors_sign}{authors_diff}"
    )

    # Files
    files_diff = stats2.total_files_changed - stats1.total_files_changed
    files_sign = "+" if files_diff > 0 else ""
    typer.echo(
        f"{'Files Changed':<30} {stats1.total_files_changed:<20} {stats2.total_files_changed:<20} {files_sign}{files_diff}"
    )

    # Lines added
    insertions_diff = stats2.total_insertions - stats1.total_insertions
    insertions_sign = "+" if insertions_diff > 0 else ""
    typer.echo(
        f"{'Lines Added':<30} {stats1.total_insertions:<20} {stats2.total_insertions:<20} {insertions_sign}{insertions_diff}"
    )

    # Lines deleted
    deletions_diff = stats2.total_deletions - stats1.total_deletions
    deletions_sign = "+" if deletions_diff > 0 else ""
    typer.echo(
        f"{'Lines Deleted':<30} {stats1.total_deletions:<20} {stats2.total_deletions:<20} {deletions_sign}{deletions_diff}"
    )

    # Net lines
    net_diff = stats2.net_lines - stats1.net_lines
    net_sign = "+" if net_diff > 0 else ""
    typer.echo(
        f"{'Net Lines':<30} {stats1.net_lines:<20} {stats2.net_lines:<20} {net_sign}{net_diff}"
    )

    typer.echo()

    # Calculate percentage changes
    if stats1.total_commits > 0:
        commits_pct = (commits_diff / stats1.total_commits) * 100
        typer.echo(f"📈 Change in commits: {commits_pct:+.1f}%")
    elif stats2.total_commits > 0:
        typer.echo("📈 Change in commits: New activity in period 2!")

    if stats1.total_insertions > 0:
        insertions_pct = (insertions_diff / stats1.total_insertions) * 100
        typer.echo("📈 Change in productivity (lines added): {insertions_pct:+.1f}%")
    elif stats2.total_insertions > 0:
        typer.echo("📈 Change in productivity: New activity in period 2!")

    typer.echo()
