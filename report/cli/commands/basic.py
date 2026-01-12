"""Basic report commands (daily, yesterday, weekly, lastweek, range)"""

from datetime import date as date_module

import typer

from report.cli.formatters import print_simple_report
from report.cli.handlers import (
    generate_custom_range_team_report,
    generate_team_report,
    handle_detailed_report,
    handle_export,
    prepare_grouped_commits_for_export,
)
from report.git.commits import get_commits, get_commits_detailed
from report.utils.categorizer import group_commits_by_component
from report.utils.dates import (
    custom_range,
    last_n_days_range,
    last_week_range,
    month_range,
    this_week_range,
    today_range,
    yesterday_range,
)

app = typer.Typer()


@app.command()
def daily(
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Summarize commits using AI",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author (use 'me' for current git user, 'all' for team report)",
    ),
    team: bool = typer.Option(
        False,
        "--team",
        "-t",
        help="Show team report with all members",
    ),
    export: str = typer.Option(
        None,
        "--export",
        "-e",
        help="Export format: json, markdown, html, email",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not specified)",
    ),
):
    """Generate daily report"""
    since, until = today_range()

    # Team mode - show all authors
    if team or (author and author.lower() == "all"):
        generate_team_report(since, until, "daily", summarize)
        return

    # Get detailed info for table
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo("No commits today.")
        raise typer.Exit(code=0)

    # Handle export if requested
    if export:
        metadata = {
            "title": "Today's Commits",
            "date_range": f"{since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}",
            "author": author if author else "All authors",
        }
        handle_export(commits_info, export, output, metadata)
        return

    # Build title
    title_prefix = "📊 Today's Commits" if summarize else "Today's commits"
    title = f"{title_prefix} (by {author})" if author else title_prefix

    if summarize:
        commits_messages = [c.message for c in commits_info]
        handle_detailed_report(commits_info, commits_messages, title, "daily", summarize)
    else:
        commits = get_commits(".", since, until, author)
        print_simple_report(commits, title)


@app.command()
def yesterday(
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Summarize commits using AI",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author (use 'me' for current git user, 'all' for team report)",
    ),
    team: bool = typer.Option(
        False,
        "--team",
        "-t",
        help="Show team report with all members",
    ),
    export: str = typer.Option(
        None,
        "--export",
        "-e",
        help="Export format: json, markdown, html, email",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not specified)",
    ),
):
    """Generate yesterday's report"""
    since, until = yesterday_range()

    # Team mode - show all authors
    if team or (author and author.lower() == "all"):
        generate_team_report(since, until, "daily", summarize)
        return

    # Get detailed info for table
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo("No commits yesterday.")
        raise typer.Exit(code=0)

    # Handle export if requested
    if export:
        metadata = {
            "title": "Yesterday's Commits",
            "date_range": f"{since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}",
            "author": author if author else "All authors",
        }
        handle_export(commits_info, export, output, metadata)
        return

    # Build title
    title_prefix = "📊 Yesterday's Commits" if summarize else "Yesterday's commits"
    title = f"{title_prefix} (by {author})" if author else title_prefix

    if summarize:
        commits_messages = [c.message for c in commits_info]
        handle_detailed_report(commits_info, commits_messages, title, "daily", summarize)
    else:
        commits = get_commits(".", since, until, author)
        print_simple_report(commits, title)


@app.command()
def weekly(
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Summarize commits using AI",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author (use 'me' for current git user, 'all' for team report)",
    ),
    team: bool = typer.Option(
        False,
        "--team",
        "-t",
        help="Show team report with all members",
    ),
    export: str = typer.Option(
        None,
        "--export",
        "-e",
        help="Export format: json, markdown, html, email",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not specified)",
    ),
):
    """Generate weekly report"""
    since, until = this_week_range()

    # Team mode - show all authors
    if team or (author and author.lower() == "all"):
        generate_team_report(since, until, "weekly", summarize)
        return

    # Get detailed info for table
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo("No commits this week.")
        raise typer.Exit(code=0)

    # Group commits by component
    commits_messages = [c.message for c in commits_info]
    grouped = group_commits_by_component(commits_messages)

    # Handle export if requested
    if export:
        grouped_info = prepare_grouped_commits_for_export(commits_info, grouped)
        metadata = {
            "title": "This Week's Commits",
            "date_range": f"{since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}",
            "author": author if author else "All authors",
        }
        handle_export(commits_info, export, output, metadata, grouped_info)
        return

    # Build title
    title_prefix = "📊 This Week's Commits" if summarize else "This week's commits"
    title = f"{title_prefix} (by {author})" if author else title_prefix

    if summarize:
        handle_detailed_report(
            commits_info, commits_messages, title, "weekly", summarize, group_by_component=True
        )
    else:
        commits = get_commits(".", since, until, author)
        print_simple_report(commits, title)


@app.command()
def lastweek(
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Summarize commits using AI",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author (use 'me' for current git user, 'all' for team report)",
    ),
    team: bool = typer.Option(
        False,
        "--team",
        "-t",
        help="Show team report with all members",
    ),
    export: str = typer.Option(
        None,
        "--export",
        "-e",
        help="Export format: json, markdown, html, email",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not specified)",
    ),
):
    """Generate last week's report"""
    since, until = last_week_range()

    # Team mode - show all authors
    if team or (author and author.lower() == "all"):
        generate_team_report(since, until, "weekly", summarize)
        return

    # Get detailed info for table
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo("No commits last week.")
        raise typer.Exit(code=0)

    # Group commits by component
    commits_messages = [c.message for c in commits_info]
    grouped = group_commits_by_component(commits_messages)

    # Handle export if requested
    if export:
        grouped_info = prepare_grouped_commits_for_export(commits_info, grouped)
        metadata = {
            "title": "Last Week's Commits",
            "date_range": f"{since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}",
            "author": author if author else "All authors",
        }
        handle_export(commits_info, export, output, metadata, grouped_info)
        return

    # Build title
    title_prefix = "📊 Last Week's Commits" if summarize else "Last week's commits"
    title = f"{title_prefix} (by {author})" if author else title_prefix

    if summarize:
        handle_detailed_report(
            commits_info, commits_messages, title, "weekly", summarize, group_by_component=True
        )
    else:
        commits = get_commits(".", since, until, author)
        print_simple_report(commits, title)


@app.command()
def range(
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
    summarize: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Summarize commits using AI",
    ),
    author: str = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author (use 'me' for current git user, 'all' for team report)",
    ),
    team: bool = typer.Option(
        False,
        "--team",
        help="Show team report with all members",
    ),
    export: str = typer.Option(
        None,
        "--export",
        "-e",
        help="Export format: json, markdown, html, email",
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not specified)",
    ),
):
    """Generate report for custom date range"""
    # Determine date range
    try:
        if from_date and to_date:
            since, until = custom_range(from_date, to_date)
            period_desc = f"{from_date} to {to_date}"
        elif days:
            since, until = last_n_days_range(days)
            period_desc = f"last {days} days"
        elif month:
            current_year = year if year else date_module.today().year
            since, until = month_range(current_year, month)
            period_desc = f"{current_year}-{month:02d}"
        else:
            typer.echo(
                "Error: Please specify date range using --from/--to, --days, or --month", err=True
            )
            typer.echo("\nExamples:")
            typer.echo("  report range --from 2024-01-01 --to 2024-01-31")
            typer.echo("  report range --days 7")
            typer.echo("  report range --month 12 --year 2024")
            raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    # Team mode - show all authors
    if team or (author and author.lower() == "all"):
        generate_custom_range_team_report(since, until, period_desc, summarize)
        return

    # Individual or filtered report
    commits_info = get_commits_detailed(".", since, until, author)

    if not commits_info:
        typer.echo(f"No commits found for period: {period_desc}")
        raise typer.Exit(code=0)

    # Group commits by component
    commits_messages = [c.message for c in commits_info]
    grouped = group_commits_by_component(commits_messages)

    # Handle export if requested
    if export:
        grouped_info = prepare_grouped_commits_for_export(commits_info, grouped)
        metadata = {
            "title": f"Commits - {period_desc}",
            "date_range": f"{since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}",
            "author": author if author else "All authors",
        }
        handle_export(commits_info, export, output, metadata, grouped_info)
        return

    # Build title
    title_prefix = f"📊 Commits - {period_desc}" if summarize else f"Commits - {period_desc}"
    title = f"{title_prefix} (by {author})" if author else title_prefix

    if summarize:
        handle_detailed_report(
            commits_info, commits_messages, title, "weekly", summarize, group_by_component=True
        )
    else:
        commits = get_commits(".", since, until, author)
        print_simple_report(commits, title)
