"""Grammar checker tool.

Usage:
        grammar "Your sentence here"

The tool returns a single corrected, formal sentence.
"""

from typing import Optional

import typer

from shared.ai import chat_completion

app = typer.Typer(help="Check grammar and rewrite text", add_completion=True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    text: Optional[str] = typer.Argument(None, help="Text to check and improve"),
) -> None:
    """Check grammar and return a formal version.

    Example:
      grammar "Check me please"
    """

    # If a subcommand is invoked in the future, do nothing here.
    if ctx.invoked_subcommand is not None:
        return

    if text is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)

    system_prompt = (
        "You are an expert English writing assistant for developer conversations and commit messages. "
        "You fix grammar and wording while keeping the original meaning. "
        "Preserve all mentions, handles, and tags that start with '@', and any emoji or icon codes "
        "written like ':name:' exactly as they appear in the input."
    )

    user_prompt = (
        "Check the grammar and rewrite this text in a single, formal, professional tone. "
        "Improve clarity, but keep all mentions, tags, or :emoji_codes: unchanged.\n\n"
        "If there is no mentions or emoji codes, just correct the grammar and improve the wording.\n\n"
        f"Original:\n{text}\n\n"
        "Return only the corrected text, without labels, explanations, or extra commentary."
    )

    try:
        result = chat_completion(
            system_prompt,
            user_prompt,
            temperature=0.5,
            max_tokens=1000,
        )
    except ValueError as e:
        typer.echo(f"⚠️  {e}")
        raise typer.Exit(code=1)

    typer.echo(result)


def cli() -> None:
    """Entry point for `python -m grammar.main`"""

    app(prog_name="grammar")


if __name__ == "__main__":
    cli()
