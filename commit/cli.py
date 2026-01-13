"""Commit message generator - CLI commands"""

from typing import Optional

import typer

from commit.git import get_all_changes, get_staged_diff, get_staged_files, analyze_diff_for_scope
from commit.ai import generate_ai_commit_message
from commit.utils import generate_conventional_message, CONVENTIONAL_TYPES, validate_subject

app = typer.Typer(help="Generate and create high-quality conventional commit messages", add_completion=True)

__all__ = ["app", "generate", "status", "diff"]


@app.command()
def generate(
    type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help=f"Commit type: {', '.join(CONVENTIONAL_TYPES)}",
        case_sensitive=False,
    ),
    scope: Optional[str] = typer.Option(
        None,
        "--scope",
        "-s",
        help="Scope (e.g., 'auth', 'api', 'ui')",
    ),
    subject: Optional[str] = typer.Option(
        None,
        "--subject",
        "-u",
        help="Short description (subject line)",
    ),
    body: Optional[str] = typer.Option(
        None,
        "--body",
        "-b",
        help="Longer description",
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation and auto-commit"),
    ai: bool = typer.Option(False, "--ai", "-a", help="Generate commit message using AI"),
    all_changes: bool = typer.Option(False, "--all", "-A", help="Stage all changes"),
    amend: bool = typer.Option(False, "--amend", help="Amend the previous commit"),
):
    """Generate and create commit messages"""
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    try:
        if all_changes:
            repo.git.add("-A")
            typer.echo("ℹ️  Staged all changes")

        staged_diff = get_staged_diff(repo)

        if not staged_diff and not amend:
            typer.echo("❌ No staged changes found. Stage files first or use --all", err=True)
            raise typer.Exit(code=1)

        if amend:
            repo.git.commit("--amend", "--no-edit")
            typer.echo("✅ Commit amended successfully")
            raise typer.Exit(code=0)

        commit_message: Optional[str] = None

        if ai:
            diff_content = get_all_changes(repo)
            try:
                ai_message = generate_ai_commit_message(diff_content)
                typer.echo("\n🤖 AI Generated Commit Message:")
                typer.echo("-" * 50)
                typer.echo(ai_message)
                typer.echo("-" * 50)
                commit_message = typer.prompt("Edit message", default=ai_message)
            except ValueError as e:
                typer.echo(f"⚠️  {e}", err=True)
                typer.echo("ℹ️  Falling back to manual mode...")

        if not commit_message:
            commit_message = _build_commit_message(type, scope, subject, body, staged_diff)

        typer.echo("\n📝 Commit Message:")
        typer.echo("-" * 50)
        typer.echo(commit_message)
        typer.echo("-" * 50)

        if not yes:
            if not typer.confirm("\nCommit these changes?"):
                typer.echo("ℹ️  Commit cancelled")
                raise typer.Exit(code=0)

        repo.index.commit(commit_message)
        typer.echo(f"✅ Commit created! Hash: {repo.head.commit.hexsha[:7]}")

    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1)


def _build_commit_message(
    type: Optional[str],
    scope: Optional[str],
    subject: Optional[str],
    body: Optional[str],
    staged_diff: str,
) -> str:
    """Build commit message interactively"""
    if type:
        type = type.lower()
        if type not in CONVENTIONAL_TYPES:
            typer.echo(f"❌ Invalid type '{type}'", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo("\nSelect commit type:")
        for i, t in enumerate(CONVENTIONAL_TYPES, 1):
            typer.echo(f"  {i}. {t}")

        choice = typer.prompt("Enter number", default="1")
        try:
            idx = int(choice) - 1
            type = CONVENTIONAL_TYPES[idx] if 0 <= idx < len(CONVENTIONAL_TYPES) else choice
        except ValueError:
            type = choice

    if not scope:
        suggested = analyze_diff_for_scope(staged_diff)
        if suggested and typer.confirm(f"Suggested scope: '{suggested}'. Use it?"):
            scope = suggested
        scope = typer.prompt("Scope (optional)", default="", show_default=False)

    if not subject:
        typer.echo("\nEnter subject (imperative mood, max 50 chars):")
        while True:
            subject_input = typer.prompt("Subject") or ""
            is_valid, error = validate_subject(subject_input)
            if is_valid:
                subject = subject_input
                break
            typer.echo(f"⚠️  {error}")

    if not body and typer.confirm("Add longer description?"):
        body = typer.prompt("Body", default="", show_default=False)

    assert type is not None, "type should not be None"
    assert subject is not None, "subject should not be None"
    return generate_conventional_message(type, scope if scope else None, subject, body)


@app.command()
def status():
    """Show staged changes"""
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    files = get_staged_files(repo)

    if not files:
        typer.echo("ℹ️  No staged files")
        raise typer.Exit(code=0)

    typer.echo(f"📂 Staged files ({len(files)}):\n")
    for f in files:
        icon = "✨" if f.status == "Added" else "📝" if f.status == "Modified" else "🗑️" if f.status == "Deleted" else "🔄"
        typer.echo(f"  {icon} [{f.status}] {f.path}")


@app.command()
def diff():
    """Show detailed diff of staged changes"""
    from git import Repo, InvalidGitRepositoryError

    try:
        repo = Repo(".", search_parent_directories=True)
    except InvalidGitRepositoryError:
        typer.echo("❌ Not a git repository", err=True)
        raise typer.Exit(code=1)

    staged_diff = get_staged_diff(repo)

    if not staged_diff:
        typer.echo("ℹ️  No staged changes")
        raise typer.Exit(code=0)

    typer.echo("📄 Diff preview:")
    typer.echo("-" * 50)
    lines = staged_diff.split("\n")[:100]
    typer.echo("\n".join(lines))
    if len(staged_diff.split("\n")) > 100:
        typer.echo(f"\n... and {len(staged_diff.split('\n')) - 100} more lines")
    typer.echo("-" * 50)
