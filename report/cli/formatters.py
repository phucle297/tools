"""Output formatting utilities for CLI"""

import typer

from report.git.commits import CommitInfo


def print_commits_table(commits_info: list[CommitInfo], title: str | None = None) -> None:
    """Print commits in a nice table format"""
    if not commits_info:
        return

    if title:
        typer.echo(f"\n{title}")

    # Calculate column widths
    hash_width = 7
    author_width = max((len(c.author) for c in commits_info), default=6)
    author_width = max(author_width, 6)  # Minimum width for "Author"
    date_width = 16
    message_width = 50

    # Header
    typer.echo(
        "┌─"
        + "─" * hash_width
        + "─┬─"
        + "─" * author_width
        + "─┬─"
        + "─" * date_width
        + "─┬─"
        + "─" * message_width
        + "─┐"
    )
    typer.echo(
        "│ "
        + "Hash".ljust(hash_width)
        + " │ "
        + "Author".ljust(author_width)
        + " │ "
        + "Date".ljust(date_width)
        + " │ "
        + "Message".ljust(message_width)
        + " │"
    )
    typer.echo(
        "├─"
        + "─" * hash_width
        + "─┼─"
        + "─" * author_width
        + "─┼─"
        + "─" * date_width
        + "─┼─"
        + "─" * message_width
        + "─┤"
    )

    # Rows
    for c in commits_info:
        msg = c.message[:47] + "..." if len(c.message) > message_width else c.message
        typer.echo(
            "│ "
            + c.hash.ljust(hash_width)
            + " │ "
            + c.author.ljust(author_width)
            + " │ "
            + c.date.ljust(date_width)
            + " │ "
            + msg.ljust(message_width)
            + " │"
        )

    # Footer
    typer.echo(
        "└─"
        + "─" * hash_width
        + "─┴─"
        + "─" * author_width
        + "─┴─"
        + "─" * date_width
        + "─┴─"
        + "─" * message_width
        + "─┘"
    )
    typer.echo()


def print_simple_report(commits: list[str], title: str) -> None:
    """Print simple list format report"""
    typer.echo(f"{title}:")
    for c in commits:
        typer.echo(f"- {c}")
