"""Extract and group commits by ticket/issue numbers"""

import re
from typing import NamedTuple

from report.git.commits import CommitInfo


class TicketCommits(NamedTuple):
    """Commits grouped by ticket"""

    ticket_id: str
    commits: list[CommitInfo]


def extract_ticket_from_message(message: str, patterns: list[str] | None = None) -> str | None:
    """Extract ticket/issue number from commit message

    Args:
        message: Commit message
        patterns: Optional list of regex patterns to match. Defaults to common patterns.

    Returns:
        Ticket ID if found, None otherwise

    Common patterns:
        - JIRA: PROJECT-123
        - GitHub: #123, GH-123
        - Linear: LIN-123
        - Generic: TICKET-123
    """
    if patterns is None:
        # Default patterns for common issue trackers
        patterns = [
            r"([A-Z]{2,10}-\d+)",  # JIRA, Linear: PROJECT-123
            r"#(\d+)",  # GitHub: #123
            r"GH-(\d+)",  # GitHub: GH-123
            r"(?:ticket|issue)[:\s]+#?(\d+)",  # Generic: ticket #123, issue: 123
        ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            # Return the full match or first group
            return match.group(1) if match.groups() else match.group(0)

    return None


def group_commits_by_ticket(
    commits_info: list[CommitInfo],
    patterns: list[str] | None = None,
) -> tuple[list[TicketCommits], list[CommitInfo]]:
    """Group commits by ticket/issue number

    Args:
        commits_info: List of commit information
        patterns: Optional custom regex patterns

    Returns:
        Tuple of (grouped_commits, unmatched_commits)
        - grouped_commits: List of TicketCommits sorted by ticket ID
        - unmatched_commits: Commits without ticket numbers
    """
    ticket_groups: dict[str, list[CommitInfo]] = {}
    unmatched: list[CommitInfo] = []

    for commit in commits_info:
        ticket_id = extract_ticket_from_message(commit.message, patterns)

        if ticket_id:
            # Normalize ticket ID (uppercase)
            ticket_id = ticket_id.upper()

            if ticket_id not in ticket_groups:
                ticket_groups[ticket_id] = []

            ticket_groups[ticket_id].append(commit)
        else:
            unmatched.append(commit)

    # Convert to list of TicketCommits, sorted by ticket ID
    grouped = [
        TicketCommits(ticket_id=ticket_id, commits=commits)
        for ticket_id, commits in sorted(ticket_groups.items())
    ]

    return grouped, unmatched


def format_ticket_summary(ticket_commits: list[TicketCommits]) -> str:
    """Format ticket summary for display

    Args:
        ticket_commits: List of TicketCommits

    Returns:
        Formatted summary string
    """
    if not ticket_commits:
        return "No tickets found in commits"

    lines = []
    lines.append(f"📋 Tickets Summary ({len(ticket_commits)} tickets):\n")

    for ticket in ticket_commits:
        lines.append(f"  {ticket.ticket_id} ({len(ticket.commits)} commits)")
        for commit in ticket.commits:
            lines.append(f"    • {commit.message[:60]}...")

    return "\n".join(lines)
