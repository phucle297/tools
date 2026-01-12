"""Export report data to various formats"""

import json
from datetime import datetime
from typing import Literal

from report.git.commits import CommitInfo

ExportFormat = Literal["json", "markdown", "html", "email"]


def export_to_json(commits_info: list[CommitInfo], metadata: dict | None = None) -> str:
    """Export commits to JSON format

    Args:
        commits_info: List of commit information
        metadata: Optional metadata (title, date range, etc.)

    Returns:
        JSON string
    """
    data = {
        "metadata": metadata or {},
        "commits": [
            {
                "hash": c.hash,
                "author": c.author,
                "date": c.date,
                "message": c.message,
            }
            for c in commits_info
        ],
        "total_commits": len(commits_info),
        "exported_at": datetime.now().isoformat(),
    }

    return json.dumps(data, indent=2, ensure_ascii=False)


def export_to_markdown(
    commits_info: list[CommitInfo],
    metadata: dict | None = None,
    grouped: dict[str, list[CommitInfo]] | None = None,
) -> str:
    """Export commits to Markdown format

    Args:
        commits_info: List of commit information
        metadata: Optional metadata (title, date range, etc.)
        grouped: Optional grouped commits by component/author

    Returns:
        Markdown string
    """
    lines = []

    # Title
    title = metadata.get("title", "Git Commit Report") if metadata else "Git Commit Report"
    lines.append(f"# {title}\n")

    # Metadata
    if metadata:
        if "date_range" in metadata:
            lines.append(f"**Period:** {metadata['date_range']}\n")
        if "author" in metadata:
            lines.append(f"**Author:** {metadata['author']}\n")
        if "team_members" in metadata:
            lines.append(f"**Team Members:** {metadata['team_members']}\n")

    lines.append(f"**Total Commits:** {len(commits_info)}\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    lines.append("---\n")

    # Commits table
    if grouped:
        # Group by component/author
        for group_name, group_commits in grouped.items():
            if not group_commits:
                continue

            lines.append(f"## {group_name} ({len(group_commits)} commits)\n")
            lines.append("| Hash | Author | Date | Message |")
            lines.append("|------|--------|------|---------|")

            for c in group_commits:
                lines.append(f"| `{c.hash}` | {c.author} | {c.date} | {c.message} |")

            lines.append("")
    else:
        # Ungrouped table
        lines.append("## Commits\n")
        lines.append("| Hash | Author | Date | Message |")
        lines.append("|------|--------|------|---------|")

        for c in commits_info:
            lines.append(f"| `{c.hash}` | {c.author} | {c.date} | {c.message} |")

    return "\n".join(lines)


def export_to_html(
    commits_info: list[CommitInfo],
    metadata: dict | None = None,
    grouped: dict[str, list[CommitInfo]] | None = None,
) -> str:
    """Export commits to HTML format

    Args:
        commits_info: List of commit information
        metadata: Optional metadata (title, date range, etc.)
        grouped: Optional grouped commits by component/author

    Returns:
        HTML string
    """
    title = metadata.get("title", "Git Commit Report") if metadata else "Git Commit Report"

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "    <meta charset='UTF-8'>",
        f"    <title>{title}</title>",
        "    <style>",
        "        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 20px; }",  # noqa: E501
        "        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }",
        "        h2 { color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }",  # noqa: E501
        "        .metadata { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }",  # noqa: E501
        "        .metadata p { margin: 5px 0; }",
        "        table { width: 100%; border-collapse: collapse; margin: 20px 0; }",
        "        th { background: #007bff; color: white; padding: 12px; text-align: left; }",
        "        td { padding: 10px; border-bottom: 1px solid #ddd; }",
        "        tr:hover { background: #f8f9fa; }",
        "        .hash { font-family: 'Courier New', monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }",  # noqa: E501
        "        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #6c757d; text-align: center; }",  # noqa: E501
        "    </style>",
        "</head>",
        "<body>",
        f"    <h1>{title}</h1>",
    ]

    # Metadata section
    if metadata:
        html.append("    <div class='metadata'>")
        if "date_range" in metadata:
            html.append(f"        <p><strong>Period:</strong> {metadata['date_range']}</p>")
        if "author" in metadata:
            html.append(f"        <p><strong>Author:</strong> {metadata['author']}</p>")
        if "team_members" in metadata:
            html.append(f"        <p><strong>Team Members:</strong> {metadata['team_members']}</p>")
        html.append(f"        <p><strong>Total Commits:</strong> {len(commits_info)}</p>")
        html.append(
            f"        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"  # noqa: E501
        )
        html.append("    </div>")

    # Commits table
    if grouped:
        for group_name, group_commits in grouped.items():
            if not group_commits:
                continue

            html.append(f"    <h2>{group_name} ({len(group_commits)} commits)</h2>")
            html.append("    <table>")
            html.append(
                "        <tr><th>Hash</th><th>Author</th><th>Date</th><th>Message</th></tr>"
            )

            for c in group_commits:
                html.append("        <tr>")
                html.append(f"            <td><span class='hash'>{c.hash}</span></td>")
                html.append(f"            <td>{c.author}</td>")
                html.append(f"            <td>{c.date}</td>")
                html.append(f"            <td>{c.message}</td>")
                html.append("        </tr>")

            html.append("    </table>")
    else:
        html.append("    <h2>Commits</h2>")
        html.append("    <table>")
        html.append("        <tr><th>Hash</th><th>Author</th><th>Date</th><th>Message</th></tr>")

        for c in commits_info:
            html.append("        <tr>")
            html.append(f"            <td><span class='hash'>{c.hash}</span></td>")
            html.append(f"            <td>{c.author}</td>")
            html.append(f"            <td>{c.date}</td>")
            html.append(f"            <td>{c.message}</td>")
            html.append("        </tr>")

        html.append("    </table>")

    html.extend(
        [
            "    <div class='footer'>",
            f"        <p>Generated by report-bot on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>",
            "    </div>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html)


def export_to_email(
    commits_info: list[CommitInfo],
    metadata: dict | None = None,
    grouped: dict[str, list[CommitInfo]] | None = None,
) -> str:
    """Export commits to email-friendly HTML format

    Args:
        commits_info: List of commit information
        metadata: Optional metadata (title, date range, etc.)
        grouped: Optional grouped commits by component/author

    Returns:
        Email-ready HTML string
    """
    title = metadata.get("title", "Git Commit Report") if metadata else "Git Commit Report"

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head><meta charset='UTF-8'></head>",
        "<body style='font-family: Arial, sans-serif; color: #333; line-height: 1.6;'>",
        f"    <h2 style='color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px;'>{title}</h2>",
    ]

    # Metadata
    if metadata:
        html.append(
            "    <div style='background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 15px 0;'>"
        )
        if "date_range" in metadata:
            html.append(
                f"        <p style='margin: 5px 0;'><strong>Period:</strong> {metadata['date_range']}</p>"
            )
        if "author" in metadata:
            html.append(
                f"        <p style='margin: 5px 0;'><strong>Author:</strong> {metadata['author']}</p>"
            )
        if "team_members" in metadata:
            html.append(
                f"        <p style='margin: 5px 0;'><strong>Team Members:</strong> {metadata['team_members']}</p>"
            )
        html.append(
            f"        <p style='margin: 5px 0;'><strong>Total Commits:</strong> {len(commits_info)}</p>"
        )
        html.append("    </div>")

    # Commits
    if grouped:
        for group_name, group_commits in grouped.items():
            if not group_commits:
                continue

            html.append(
                f"    <h3 style='color: #555; margin-top: 25px;'>{group_name} ({len(group_commits)} commits)</h3>"
            )
            html.append("    <ul style='list-style-type: none; padding-left: 0;'>")

            for c in group_commits:
                html.append(
                    "        <li style='margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 3px solid #007bff;'>"
                )
                html.append(f"            <strong>{c.message}</strong><br>")
                html.append(
                    f"            <small style='color: #666;'>{c.author} • {c.date} • <code>{c.hash}</code></small>"
                )
                html.append("        </li>")

            html.append("    </ul>")
    else:
        html.append("    <ul style='list-style-type: none; padding-left: 0;'>")

        for c in commits_info:
            html.append(
                "        <li style='margin: 10px 0; padding: 10px; background: #f9f9f9; border-left: 3px solid #007bff;'>"
            )
            html.append(f"            <strong>{c.message}</strong><br>")
            html.append(
                f"            <small style='color: #666;'>{c.author} • {c.date} • <code>{c.hash}</code></small>"
            )
            html.append("        </li>")

        html.append("    </ul>")

    html.extend(
        [
            "    <hr style='margin-top: 30px; border: none; border-top: 1px solid #ddd;'>",
            f"    <p style='color: #999; text-align: center;'><small>Generated by report-bot on {datetime.now().strftime('%Y-%m-%d %H:%M')}</small></p>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html)


def export_commits(
    commits_info: list[CommitInfo],
    format: ExportFormat,
    metadata: dict | None = None,
    grouped: dict[str, list[CommitInfo]] | None = None,
) -> str:
    """Export commits to specified format

    Args:
        commits_info: List of commit information
        format: Export format (json, markdown, html, email)
        metadata: Optional metadata
        grouped: Optional grouped commits

    Returns:
        Exported content as string
    """
    if format == "json":
        return export_to_json(commits_info, metadata)
    elif format == "markdown":
        return export_to_markdown(commits_info, metadata, grouped)
    elif format == "html":
        return export_to_html(commits_info, metadata, grouped)
    elif format == "email":
        return export_to_email(commits_info, metadata, grouped)
    else:
        raise ValueError(f"Unsupported export format: {format}")
