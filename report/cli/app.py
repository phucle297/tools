"""CLI application setup and command registration"""

import typer

from report.cli import completion
from report.cli.commands import advanced, basic, stats
from report.cli.commands import config as config_cmd

# Create main app
app = typer.Typer(help="Daily & Weekly Report CLI")

# Register basic commands (daily, yesterday, weekly, lastweek, range)
app.command(name="daily")(basic.daily)
app.command(name="yesterday")(basic.yesterday)
app.command(name="weekly")(basic.weekly)
app.command(name="lastweek")(basic.lastweek)
app.command(name="range")(basic.range)

# Register stats commands
app.command(name="stats")(stats.stats)
app.command(name="compare")(stats.compare)

# Register advanced commands
app.command(name="filter")(advanced.filter)
app.command(name="search")(advanced.search)
app.command(name="multirepo")(advanced.multirepo)
app.command(name="tickets")(advanced.tickets)

# Register config command
app.command(name="config")(config_cmd.config)

# Register completion command (as a subcommand group)
app.add_typer(completion.completion_app, name="completion")
