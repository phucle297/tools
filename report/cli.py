import typer

from report.git.commits import get_commits
from report.utils.dates import this_week_range, today_range

app = typer.Typer(help="Daily & Weekly Report CLI")


@app.command()
def daily():
    """Generate daily report"""
    since, until = today_range()
    commits = get_commits(".", since, until)

    if not commits:
        typer.echo("No commits today.")
        raise typer.Exit(code=0)

    typer.echo("Today's commits:")
    for c in commits:
        typer.echo(f"- {c}")


@app.command()
def weekly():
    """Generate weekly report"""
    since, until = this_week_range()
    commits = get_commits(".", since, until)

    if not commits:
        typer.echo("No commits this week.")
        raise typer.Exit(code=0)

    typer.echo("This week's commits:")
    for c in commits:
        typer.echo(f"- {c}")


def main():
    app()


if __name__ == "__main__":
    main()
