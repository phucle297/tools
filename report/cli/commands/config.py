"""Configuration management command"""

import json

import typer

from report.utils.config import get_config_path, init_config, load_config

app = typer.Typer()


@app.command()
def config(
    action: str = typer.Argument(
        "show",
        help="Action: init (create config), show (display config), path (show config path)",
    ),
):
    """Manage configuration file"""
    if action == "init":
        init_config()
    elif action == "show":
        config_data = load_config()
        typer.echo("\n📋 Current Configuration:\n")
        typer.echo(json.dumps(config_data, indent=2))
        typer.echo(f"\n📁 Config file: {get_config_path()}")
    elif action == "path":
        typer.echo(get_config_path())
    else:
        typer.echo(f"Error: Unknown action '{action}'. Use: init, show, or path", err=True)
        raise typer.Exit(code=1)
