# report-bot

A comprehensive CLI tool for lazy developers to generate beautiful git commit reports with AI-powered summarization.

Perfect for **team leaders** who need to:
- Track team productivity
- Generate reports for stakeholders
- Catch up on team member progress
- Analyze git statistics

## Features

### 📊 Core Reporting
- **Daily Reports**: View commits made today or yesterday
- **Weekly Reports**: View commits made this week or last week
- **Custom Date Range**: Generate reports for any time period
- **Beautiful Tables**: Commits displayed in formatted tables with hash, author, date, and message

### 👥 Team Features
- **Team Reports**: Show all team members' commits in one report (`--team`)
- **Author Filtering**: Filter commits by specific author (`--author "name"`)
- **"Me" Keyword**: Use `--author me` to show only your commits
- **Per-Author Statistics**: See individual contributions

### 🤖 AI-Powered
- **AI Summarization**: Get AI-powered summaries organized by categories
- **Component Grouping**: Automatic categorization (Console/Server/Others)
- **Professional Reports**: Manager-friendly summaries ready to send

### 📈 Analytics & Statistics
- **Git Statistics**: View detailed metrics (commits, files, lines added/deleted)
- **Team Analytics**: Compare team member contributions
- **Productivity Insights**: Track trends over time

### 🎯 Export & Integration
- **Multiple Formats**: Export to JSON, Markdown, HTML, or Email-ready format
- **Ticket Tracking**: Extract and group commits by JIRA/GitHub issue numbers
- **Component Analysis**: Group commits by codebase component

## Prerequisites

This repository requires to install nix direnv

- https://github.com/nix-community/nix-direnv

## Installation

You can use pipx to install the cli tool:

```bash
pipx install -e .
```

## Reinstall after changes

```bash
pipx uninstall report-bot && pipx install -e .
```

## Configuration

### Shell Completion (Recommended)

Enable tab completion for the `report` command:

```bash
# Auto-detect your shell and install completion
report completion install

# Or specify your shell explicitly
report completion install --shell bash   # For Bash
report completion install --shell zsh    # For Zsh
report completion install --shell fish   # For Fish

# Show completion script (without installing)
report completion show
```

**For Bash users:**
After installation, add this line to your `~/.bashrc`:
```bash
source ~/.bash_completions/report.sh
```
Then run: `source ~/.bashrc`

**For Zsh users:**
Add these lines to your `~/.zshrc`:
```zsh
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```
Then run: `source ~/.zshrc`

**For Fish users:**
Just restart your terminal or run:
```fish
source ~/.config/fish/config.fish
```

### AI Summarization (Optional)

To use the AI-powered commit summarization feature, you need to set up a Groq API key:

1. Get a free API key from: https://console.groq.com/keys
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

## Usage

After install globally, you can use the cli tool `report`

### Basic Commands

```bash
# Show help
report --help

# Generate today's report
report daily

# Generate yesterday's report
report yesterday

# Generate this week's report
report weekly

# Generate last week's report
report lastweek
```

### Team Leader Features

```bash
# Team report showing all members
report daily --team
report weekly --team

# Filter by specific author
report daily --author "John Doe"
report weekly --author "Jane"

# Show only your commits
report daily --author me

# Team report with AI summary
report weekly --team --summarize
```

### Custom Date Ranges

```bash
# Last 7 days
report range --days 7

# Last 30 days
report range --days 30

# Specific date range
report range --from 2024-01-01 --to 2024-01-31

# Specific month
report range --month 12 --year 2024

# With AI summary
report range --days 7 --summarize

# Team report for custom range
report range --days 14 --team --summarize
```

### Git Statistics

```bash
# Stats for today
report stats

# Stats for this week
report stats weekly

# Stats for last 30 days
report stats --days 30

# Stats for specific author
report stats weekly --author "John Doe"

# Team stats
report stats weekly
```

### AI Summarization

Add `--summarize` or `-s` to any command:

```bash
report daily --summarize
report weekly -s
report range --days 7 -s
```

### Advanced Commands

```bash
# Compare two time periods
report compare thisweek lastweek
report compare today yesterday
report compare --from1 2024-01-01 --to1 2024-01-31 --from2 2024-02-01 --to2 2024-02-28

# Filter commits with advanced options
report filter --days 7 --include "fix,bug"
report filter --days 14 --exclude "merge,wip" --author me
report filter --days 30 --files  # Show files changed in each commit

# Search for specific keywords in commits
report search "bug" --days 30
report search "feature" --author me --case-sensitive

# Multi-repository reports
report multirepo --workspace ~/projects --discover
report multirepo --repos /path/repo1,/path/repo2 --days 7

# Ticket/Issue tracking
report tickets --days 7
report tickets --from 2024-01-01 --to 2024-01-31 --author me
report tickets --patterns "PROJ-\d+,TICKET-\d+"  # Custom patterns

# Configuration management
report config init    # Create config file
report config show    # Display current config
report config path    # Show config file location

# Shell completion management
report completion install              # Install for current shell
report completion install --shell bash # Install for bash
report completion show                 # Show completion script
```

### Export Reports

```bash
# Export to different formats
report daily --export json --output report.json
report weekly --export markdown --output report.md
report range --days 30 --export html --output report.html
report weekly --team --export email --output email.html
```

## Command Reference

### `report daily`
Generate daily report with optional AI summarization
- `--summarize, -s`: Add AI summary
- `--author, -a NAME`: Filter by author (use "me" for yourself)
- `--team, -t`: Show all team members

### `report yesterday`
Same options as daily, but for yesterday

### `report weekly`
Generate weekly report (Monday-Sunday)
- `--summarize, -s`: Add AI summary with component grouping
- `--author, -a NAME`: Filter by author
- `--team, -t`: Show all team members

### `report lastweek`
Same options as weekly, but for last week

### `report range`
Generate report for custom date range
- `--from, -f DATE`: Start date (YYYY-MM-DD)
- `--to, -t DATE`: End date (YYYY-MM-DD)
- `--days, -d N`: Last N days
- `--month, -m N`: Month number (1-12)
- `--year, -y YEAR`: Year (use with --month)
- `--summarize, -s`: Add AI summary
- `--author, -a NAME`: Filter by author
- `--team`: Show all team members
- `--export, -e FORMAT`: Export format (json, markdown, html, email)
- `--output, -o FILE`: Output file path

### `report stats`
Show git statistics and analytics
- `PERIOD`: daily, yesterday, weekly, lastweek (default: daily)
- `--from, -f DATE`: Start date
- `--to, -t DATE`: End date
- `--days, -d N`: Last N days
- `--month, -m N`: Month number
- `--year, -y YEAR`: Year
- `--author, -a NAME`: Filter by author

### `report compare`
Compare git statistics between two time periods
- `PERIOD1`: First period (thisweek, lastweek, today, yesterday, or use --from1/--to1)
- `PERIOD2`: Second period
- `--from1 DATE`: Start date for period 1
- `--to1 DATE`: End date for period 1
- `--from2 DATE`: Start date for period 2
- `--to2 DATE`: End date for period 2
- `--author, -a NAME`: Filter by author

### `report filter`
Filter commits with advanced options
- `--days, -d N`: Filter commits from last N days (default: 7)
- `--author, -a NAME`: Filter by author
- `--exclude, -x KEYWORDS`: Exclude commits matching keywords (comma-separated)
- `--include, -i KEYWORDS`: Include only commits matching keywords (comma-separated)
- `--files, -f`: Show files changed in each commit

### `report search`
Search commits by keyword
- `KEYWORD`: Keyword to search in commit messages
- `--days, -d N`: Search in last N days (default: 30)
- `--author, -a NAME`: Filter by author
- `--case-sensitive, -c`: Case-sensitive search

### `report multirepo`
Generate report across multiple repositories
- `--workspace, -w DIR`: Workspace directory containing multiple repos
- `--repos, -r PATHS`: Comma-separated list of repository paths
- `--days, -d N`: Last N days (default: 7)
- `--author, -a NAME`: Filter by author
- `--discover`: Auto-discover repositories in workspace

### `report tickets`
Show commits grouped by ticket/issue numbers
- `--from, -f DATE`: Start date
- `--to, -t DATE`: End date
- `--days, -d N`: Last N days (default: 7)
- `--author, -a NAME`: Filter by author
- `--patterns, -p PATTERNS`: Custom regex patterns (comma-separated)

### `report config`
Manage configuration file
- `ACTION`: init (create), show (display), or path (show location)

### `report completion`
Manage shell completion
- `install` - Install shell completion for current or specified shell
  - `--shell SHELL`: Specify shell type (bash, zsh, fish)
- `show` - Show completion script for current or specified shell
  - `--shell SHELL`: Specify shell type (bash, zsh, fish)

## Examples

### For Team Leaders

```bash
# Monday morning: Check what team did last week
report lastweek --team --summarize

# Daily standup: Quick team update
report daily --team

# End of sprint: Comprehensive team stats
report stats --days 14

# Check specific team member's work
report weekly --author "John Doe" --summarize

# Generate report for stakeholders
report range --from 2024-01-01 --to 2024-01-31 --team --summarize > report.txt
```

### For Individual Developers

```bash
# What did I do today?
report daily --author me

# My weekly summary
report weekly --author me --summarize

# My productivity stats
report stats weekly --author me

# Search my bug fixes
report search "fix" --author me --days 30

# Export my work summary
report range --days 14 --author me --export markdown --output my-work.md
```

### Advanced Usage Examples

```bash
# Compare this week vs last week productivity
report compare thisweek lastweek

# Find all commits related to a feature
report search "authentication" --days 60

# Filter out work-in-progress commits
report filter --days 7 --exclude "wip,draft"

# Generate report across multiple projects
report multirepo --workspace ~/projects --discover --days 7

# Track JIRA tickets in commits
report tickets --days 14 --author me

# Export team report as email
report weekly --team --export email --output team-report.html
```

## Tips & Best Practices

1. **Enable shell completion** for faster command usage:
   ```bash
   # Install once, use forever
   report completion install
   
   # Then restart your terminal and enjoy tab completion:
   report <TAB>              # Shows all commands
   report daily --<TAB>      # Shows all options for daily command
   report stats <TAB>        # Shows period options
   ```

2. **Use aliases** for frequently used commands:
   ```bash
   alias today="report daily --author me --summarize"
   alias myweek="report weekly --author me --summarize"
   alias teamweek="report weekly --team --summarize"
   alias mystats="report stats weekly --author me"
   ```

3. **Export reports** for stakeholders:
   ```bash
   # Weekly team report as HTML
   report weekly --team --summarize --export html --output weekly.html
   
   # Monthly report as Markdown
   report range --month 1 --year 2024 --export markdown --output jan-2024.md
   ```

4. **Combine with other tools**:
   ```bash
   # Count total commits
   report weekly | grep -c "^-"
   
   # Search for specific keywords
   report weekly | grep -i "bug"
   
   # Pipe to less for long reports
   report range --days 30 | less
   ```

5. **Use configuration file** for team settings:
   ```bash
   # Initialize config
   report config init
   
   # Edit ~/.config/report-bot/config.json to add:
   # - Team member names
   # - Component categorization keywords
   # - Custom ticket patterns
   # - Default options
   ```

6. **Compare productivity** between time periods:
   ```bash
   # This month vs last month
   report compare --from1 2024-01-01 --to1 2024-01-31 \
                   --from2 2024-02-01 --to2 2024-02-29
   ```

7. **Track specific features** using search and filter:
   ```bash
   # Find all authentication-related work
   report search "auth" --days 90
   
   # Show only feature commits (exclude fixes)
   report filter --days 14 --include "feat,feature" --author me
   ```

The AI summarization feature uses Groq's fast and free API to provide professional, categorized summaries of your git commits.
