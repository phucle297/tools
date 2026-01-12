"""Report generation and handling logic"""

from datetime import datetime
from typing import Optional

import typer

from report.ai.summarizer import AICommitSummarizer
from report.cli.formatters import print_commits_table
from report.git.commits import CommitInfo, get_all_authors, get_commits_detailed
from report.utils.categorizer import ComponentType, group_commits_by_component
from report.utils.exporters import ExportFormat, export_commits

# Constants
COMPONENT_ORDER: list[ComponentType] = ["Console", "Server", "Others"]


def handle_export(
    commits_info: list[CommitInfo],
    export_format: Optional[str],
    output_file: Optional[str],
    metadata: Optional[dict] = None,
    grouped: Optional[dict] = None,
) -> None:
    """Handle export of commits to file"""
    if not export_format:
        return

    # Validate format
    valid_formats: list[ExportFormat] = ["json", "markdown", "html", "email"]
    if export_format not in valid_formats:
        typer.echo(
            f"Error: Invalid export format. Must be one of: {', '.join(valid_formats)}", err=True
        )
        raise typer.Exit(code=1)

    # Export
    try:
        content = export_commits(commits_info, export_format, metadata, grouped)  # type: ignore

        # Write to file or stdout
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            typer.echo(f"\n✓ Report exported to {output_file}")
        else:
            typer.echo("\n" + "=" * 80)
            typer.echo(content)
            typer.echo("=" * 80)
    except Exception as e:
        typer.echo(f"Error exporting report: {e}", err=True)
        raise typer.Exit(code=1)


def generate_ai_summary(
    commits_messages: list[str], report_type: str, grouped_dict: dict[str, list[str]] | None = None
) -> None:
    """Generate and print AI summary"""
    typer.echo("🤖 AI Summary:\n")
    try:
        summarizer = AICommitSummarizer()
        summary = summarizer.summarize(
            commits_messages, report_type=report_type, grouped=grouped_dict
        )
        typer.echo(summary)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)


def handle_detailed_report(
    commits_info: list[CommitInfo],
    commits_messages: list[str],
    title: str,
    report_type: str,
    summarize: bool,
    group_by_component: bool = False,
) -> None:
    """Handle detailed report with optional summarization and grouping"""
    typer.echo(f"{title}:\n")

    if group_by_component:
        # Group by component
        grouped = group_commits_by_component(commits_messages)

        for component in COMPONENT_ORDER:
            component_commits = grouped.get(component, [])
            if component_commits:
                component_info = [c for c in commits_info if c.message in component_commits]
                print_commits_table(component_info, title=f"  {component}")

        if summarize:
            grouped_dict = {k: v for k, v in grouped.items()}
            generate_ai_summary(commits_messages, report_type, grouped_dict)
    else:
        # Simple table
        print_commits_table(commits_info)

        if summarize:
            generate_ai_summary(commits_messages, report_type)


def prepare_grouped_commits_for_export(
    commits_info: list[CommitInfo], grouped: dict[ComponentType, list[str]]
) -> dict[str, list[CommitInfo]]:
    """Prepare grouped commits info for export"""
    grouped_info = {}
    for component in COMPONENT_ORDER:
        component_commits = grouped.get(component, [])
        if component_commits:
            grouped_info[component] = [c for c in commits_info if c.message in component_commits]
    return grouped_info


def generate_team_report(
    since: datetime, until: datetime, report_type: str, summarize: bool = False
) -> None:
    """Generate report for all team members"""
    # Get all authors
    authors = get_all_authors(".", since, until)

    if not authors:
        typer.echo("No team members found in this time period.")
        raise typer.Exit(code=0)

    typer.echo(f"📊 Team Report - {report_type.title()}\n")
    typer.echo(f"👥 Team Members ({len(authors)}):")

    # Collect all commits and organize by author
    all_commits_info: list[CommitInfo] = []
    commits_by_author: dict[str, list[CommitInfo]] = {}

    for author in authors:
        commits_info = get_commits_detailed(".", since, until, author)
        if commits_info:
            commits_by_author[author] = commits_info
            all_commits_info.extend(commits_info)
            typer.echo(f"├─ {author}: {len(commits_info)} commits")

    typer.echo()

    if not all_commits_info:
        typer.echo("No commits found for any team member.")
        raise typer.Exit(code=0)

    # Show commits grouped by author
    for author in authors:
        if author in commits_by_author:
            print_commits_table(commits_by_author[author], title=f"  {author}")

    # AI Summary if requested
    if summarize:
        commits_messages = [c.message for c in all_commits_info]

        # Group by component for weekly reports
        if report_type == "weekly":
            grouped = group_commits_by_component(commits_messages)
            grouped_dict = {k: v for k, v in grouped.items()}
            generate_ai_summary(commits_messages, report_type, grouped_dict)
        else:
            generate_ai_summary(commits_messages, report_type)


def generate_custom_range_team_report(
    since: datetime, until: datetime, period_desc: str, summarize: bool
) -> None:
    """Generate custom range team report"""
    typer.echo(f"📊 Team Report - {period_desc}\n")

    # Get all authors
    authors = get_all_authors(".", since, until)

    if not authors:
        typer.echo("No team members found in this time period.")
        raise typer.Exit(code=0)

    typer.echo(f"👥 Team Members ({len(authors)}):")

    # Collect all commits and organize by author
    all_commits_info: list[CommitInfo] = []
    commits_by_author: dict[str, list[CommitInfo]] = {}

    for author_name in authors:
        commits_info = get_commits_detailed(".", since, until, author_name)
        if commits_info:
            commits_by_author[author_name] = commits_info
            all_commits_info.extend(commits_info)
            typer.echo(f"├─ {author_name}: {len(commits_info)} commits")

    typer.echo()

    if not all_commits_info:
        typer.echo("No commits found for any team member.")
        raise typer.Exit(code=0)

    # Show commits grouped by author
    for author_name in authors:
        if author_name in commits_by_author:
            print_commits_table(commits_by_author[author_name], title=f"  {author_name}")

    # AI Summary if requested
    if summarize:
        commits_messages = [c.message for c in all_commits_info]
        grouped = group_commits_by_component(commits_messages)
        grouped_dict = {k: v for k, v in grouped.items()}
        generate_ai_summary(commits_messages, "weekly", grouped_dict)
