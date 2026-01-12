# AGENTS.md

## Project Overview

**Project Name:** report-bot  
**Description:** Comprehensive Git Report CLI tool for lazy developers and team leaders  
**Version:** 0.3.0

This is a Python-based CLI tool that generates daily, weekly, and custom-range reports of git commits from a repository with optional AI-powered summarization. Designed specifically for team leaders who need to track team productivity, generate reports for stakeholders, and analyze git statistics.

## Project Structure

```
.
├── report/
│   ├── __init__.py
│   ├── main.py                # Main entry point
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py             # CLI application setup and command registration
│   │   ├── completion.py      # Shell completion management
│   │   ├── formatters.py      # Output formatting utilities
│   │   ├── handlers.py        # Report generation and handling logic
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── basic.py       # Basic report commands (daily, yesterday, weekly, etc.)
│   │       ├── advanced.py    # Advanced commands (filter, search, multirepo, tickets)
│   │       ├── stats.py       # Statistics and comparison commands
│   │       └── config.py      # Configuration management command
│   ├── ai/
│   │   ├── __init__.py
│   │   └── summarizer.py      # AI-powered commit summarization
│   ├── git/
│   │   ├── __init__.py
│   │   └── commits.py         # Git commit retrieval logic
│   └── utils/
│       ├── __init__.py
│       ├── categorizer.py     # Commit categorization by component
│       ├── config.py          # Configuration management
│       ├── dates.py           # Date range utilities
│       ├── exporters.py       # Export to multiple formats
│       ├── stats.py           # Git statistics and analytics
│       └── tickets.py         # Ticket/JIRA integration
├── tests/
│   ├── conftest.py
│   ├── unit/                  # Unit tests for individual modules
│   └── integration/           # Integration tests for CLI
├── bin/
│   └── report                 # Binary entry point (bash wrapper)
├── pyproject.toml             # Project configuration and dependencies
├── requirements.txt           # Python dependencies
├── shell.nix                  # Nix shell configuration
├── .envrc                     # direnv configuration
├── .env.example               # Example environment configuration
├── AGENTS.md                  # This file - Project documentation for AI agents
└── README.md                  # User-facing project documentation
```

## Core Components

### 1. Main Entry Point (`report/main.py`)

**Purpose:** Entry point that initializes the CLI application with proper program name

**Function:**

#### `main()`

Main entry point that calls the Typer app with `prog_name="report"` to ensure proper shell completion support.

### 2. CLI Application (`report/cli/app.py`)

**Purpose:** CLI application setup and command registration using Typer framework

**Commands:**
- `daily` - Generates a report of commits made today
- `yesterday` - Generates a report of commits made yesterday
- `weekly` - Generates a report of commits made this week (Monday-Sunday)
- `lastweek` - Generates a report of commits made last week (Monday-Sunday)
- `range` - Generates a report for custom date range (with --from/--to, --days, or --month)
- `stats` - Shows git statistics and analytics for any time period
- `compare` - Compares git statistics between two time periods
- `filter` - Filters commits with advanced options (include/exclude keywords)
- `search` - Searches commits by keyword
- `multirepo` - Generates report across multiple repositories
- `tickets` - Shows commits grouped by ticket/issue numbers
- `config` - Manages configuration file
- `completion` - Shell completion installation and management

**Structure:**
- Creates main Typer app
- Registers commands from command modules (basic, advanced, stats, config)
- Registers completion subcommand group

**Dependencies:**
- `typer` - CLI framework
- `report.cli.commands` - Command modules
- `report.cli.completion` - Completion management

### 3. CLI Commands Module (`report/cli/commands/`)

**Purpose:** Organized command implementations split by category

#### Basic Commands (`basic.py`)

Commands: `daily`, `yesterday`, `weekly`, `lastweek`, `range`

**Common Options:**
- `--summarize, -s`: Enable AI-powered summarization
- `--author, -a NAME`: Filter by author name (use "me" for current git user, "all" for team report)
- `--team, -t`: Show team report with all members
- `--export, -e FORMAT`: Export format (json, markdown, html, email)
- `--output, -o FILE`: Output file path

#### Advanced Commands (`advanced.py`)

Commands: `filter`, `search`, `multirepo`, `tickets`

**Features:**
- Advanced filtering with include/exclude patterns
- Keyword search with case sensitivity options
- Multi-repository report generation
- Ticket/issue number extraction and grouping

#### Statistics Commands (`stats.py`)

Commands: `stats`, `compare`

**Features:**
- Detailed git statistics (commits, files, lines changed)
- Per-author statistics with tables
- Time period comparison with delta calculations
- Support for multiple date range formats

#### Configuration Command (`config.py`)

Command: `config`

**Actions:**
- `init` - Create configuration file with defaults
- `show` - Display current configuration
- `path` - Show configuration file location

### 4. Shell Completion Module (`report/cli/completion.py`)

**Purpose:** Shell completion installation and management for bash, zsh, and fish

**Commands:**
- `completion install` - Install shell completion (auto-detects shell)
- `completion show` - Show completion script for current shell

**Features:**
- Auto-detection of shell type (bash, zsh, fish)
- Manual shell specification via `--shell` option
- Generates proper completion scripts that reference `report` command
- Provides installation instructions for each shell
- Handles completion directory creation

**Supported Shells:**
- **Bash**: Installs to `~/.bash_completions/report.sh`
- **Zsh**: Installs to `~/.zsh/completions/_report`
- **Fish**: Installs to `~/.config/fish/completions/report.fish`

**Functions:**

#### `install(shell: str | None = None)`

Installs shell completion for the report command.

**Parameters:**
- `shell` - Shell type (bash, zsh, fish), auto-detected if None

**Behavior:**
- Auto-detects shell from $SHELL environment variable
- Creates completion directory if needed
- Generates shell-specific completion script
- Provides setup instructions for sourcing completion

#### `show(shell: str | None = None)`

Shows the completion script for the specified or detected shell.

**Parameters:**
- `shell` - Shell type (bash, zsh, fish), auto-detected if None

#### Helper Functions:
- `install_bash_completion()` - Generates bash completion using Typer's completion format
- `install_zsh_completion()` - Generates zsh completion with fpath configuration
- `install_fish_completion()` - Generates fish completion using Typer's fish format

**Technical Details:**
- Uses Typer's completion system with environment variable `_REPORT_COMPLETE`
- Bash completion format: `_REPORT_COMPLETE=complete_bash`
- Fish completion format: Uses Typer's fish-specific completion commands
- Proper program name (`report`) set in main.py via `app(prog_name="report")`

### 5. CLI Formatters (`report/cli/formatters.py`)

**Purpose:** Output formatting utilities for commit display

**Functions:**

#### `print_commits_table(commits_info: list[CommitInfo], title: str | None = None) -> None`

Prints commits in a formatted table with borders, showing hash, author, date, and message.

**Features:**
- Dynamic column width adjustment
- Beautiful Unicode box drawing characters
- Truncates long messages with "..."

#### `print_simple_report(commits: list[str], title: str) -> None`

Prints commits in simple bullet list format.

### 6. CLI Handlers (`report/cli/handlers.py`)

**Purpose:** Report generation and handling logic

**Functions:**

#### `handle_export(commits_info, export_format, output_file, metadata, grouped) -> None`

Handles export of commits to various formats (JSON, Markdown, HTML, Email).

#### `generate_ai_summary(commits_messages, report_type, grouped_dict) -> None`

Generates and prints AI-powered summary of commits.

#### `handle_detailed_report(commits_info, commits_messages, title, report_type, summarize, group_by_component) -> None`

Handles detailed report generation with optional AI summarization and component grouping.

#### `prepare_grouped_commits_for_export(commits_info, grouped) -> dict`

Prepares grouped commits for export by organizing CommitInfo objects by component.

#### `generate_team_report(since, until, report_type, summarize) -> None`

Generates comprehensive report showing all team members' commits.

#### `generate_custom_range_team_report(since, until, period_desc, summarize) -> None`

Generates team report for custom date ranges.

**Constants:**
- `COMPONENT_ORDER` - Defines display order: ["Console", "Server", "Others"]

### 7. CLI Module (`report/cli.py`) - DEPRECATED

**Purpose:** Main command-line interface using Typer framework

**Commands:**
- `daily` - Generates a report of commits made today
- `yesterday` - Generates a report of commits made yesterday
- `weekly` - Generates a report of commits made this week (Monday-Sunday)
- `lastweek` - Generates a report of commits made last week (Monday-Sunday)
- `range` - Generates a report for custom date range (with --from/--to, --days, or --month)
- `stats` - Shows git statistics and analytics for any time period
- `compare` - Compares git statistics between two time periods
- `filter` - Filters commits with advanced options (include/exclude keywords)
- `search` - Searches commits by keyword
- `multirepo` - Generates report across multiple repositories
- `tickets` - Shows commits grouped by ticket/issue numbers
- `config` - Manages configuration file

**Key Features:**
- User-friendly CLI with Typer
- Supports both simple list format and detailed table format
- Optional AI-powered summarization (via `--summarize` or `-s` flag)
- Beautiful table display showing commit hash, author, date, and message
- Groups commits by component (Console/Server/Others) for weekly reports
- Team mode (`--team` flag) to show all team members in one report
- Author filtering (`--author` flag) with support for "me" keyword
- Exits gracefully when no commits are found

**Common Options (available in most commands):**
- `--summarize, -s`: Enable AI-powered summarization
- `--author, -a NAME`: Filter by author name (use "me" for current git user, "all" for team report)
- `--team, -t`: Show team report with all members

**Helper Functions:**
- `_print_commits_table(commits_info, title=None)` - Prints commits in a formatted table with borders
- `_handle_simple_report(commits, title)` - Handles simple list format report
- `_handle_detailed_report(commits_info, commits_messages, title, report_type, summarize, group_by_component)` - Handles detailed report with optional summarization and grouping
- `_prepare_grouped_commits_for_export(commits_info, grouped)` - Prepares grouped commits info for export
- `_generate_ai_summary(commits_messages, report_type, grouped_dict)` - Generates and prints AI summary
- `_generate_team_report(since, until, report_type, summarize)` - Generates comprehensive team reports
- `_generate_custom_range_team_report(since, until, period_desc, summarize)` - Generates custom range team report
- `_handle_export(commits_info, export_format, output_file, metadata, grouped)` - Handles export of commits to file

**Dependencies:**
- `typer` - CLI framework
- `report.git.commits.get_commits` - Commit retrieval (messages only)
- `report.git.commits.get_commits_detailed` - Commit retrieval (detailed info)
- `report.git.commits.get_all_authors` - Get all unique authors
- `report.utils.dates` - Date range utilities
- `report.utils.categorizer.group_commits_by_component` - Component categorization
- `report.utils.stats.get_commit_stats` - Statistics generation
- `report.utils.exporters` - Export functionality
- `report.ai.summarizer.AICommitSummarizer` - AI summarization

### 8. Git Module (`report/git/commits.py`)

**Purpose:** Handles git repository operations and commit retrieval

**Data Structures:**

#### `CommitInfo` (NamedTuple)

Contains information about a single commit:
- `hash: str` - Short commit hash (7 characters)
- `author: str` - Commit author name
- `date: str` - Commit date in format "YYYY-MM-DD HH:MM"
- `message: str` - First line of commit message

**Functions:**

#### `get_commits(repo_path: str, since: datetime, until: datetime, author: str | None = None) -> list[str]`

Retrieves commit messages only from a git repository within a specified date range (for backward compatibility).

**Parameters:**
- `repo_path` - Path to the git repository
- `since` - Start datetime for commit range
- `until` - End datetime for commit range
- `author` - Optional author filter (supports "me" keyword)

**Returns:**
- List of commit message strings

#### `get_commits_detailed(repo_path: str, since: datetime, until: datetime, author: str | None = None) -> list[CommitInfo]`

Retrieves detailed commit information including hash, author, date, and message.

**Parameters:**
- `repo_path` - Path to the git repository
- `since` - Start datetime for commit range
- `until` - End datetime for commit range
- `author` - Optional author filter (supports "me" keyword for current git user)

**Returns:**
- List of CommitInfo named tuples

**Author Filtering:**
- If `author="me"`, filters commits by current git user
- Otherwise, performs case-insensitive substring match on author name

#### `get_all_authors(repo_path: str, since: datetime | None = None, until: datetime | None = None) -> list[str]`

Gets all unique authors in the repository within optional date range.

**Parameters:**
- `repo_path` - Path to git repository
- `since` - Optional start datetime
- `until` - Optional end datetime

**Returns:**
- List of unique author names sorted alphabetically

**Features:**
- Searches parent directories for git repository
- Filters out merge commits (`no_merges=True`)
- Handles both byte and string commit messages
- Extracts only first line of commit message for table display
- Proper error handling for non-git directories

**Error Handling:**
- Raises `RuntimeError` if not in a git repository

### 9. Utils Module (`report/utils/dates.py`)

**Purpose:** Provides date range utilities for report generation

**Functions:**

#### `today_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for today (00:00:00 to 23:59:59).

#### `yesterday_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for yesterday (00:00:00 to 23:59:59).

#### `this_week_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for the current week (Monday 00:00:00 to Sunday 23:59:59).

#### `last_week_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for the previous week (Monday 00:00:00 to Sunday 23:59:59).

#### `custom_range(from_date: str, to_date: str) -> tuple[datetime, datetime]`

Create custom date range from string dates.

**Parameters:**
- `from_date` - Start date in YYYY-MM-DD format
- `to_date` - End date in YYYY-MM-DD format

**Returns:**
- Tuple of (start_datetime, end_datetime)

**Raises:**
- ValueError if date format is invalid or start > end

#### `last_n_days_range(days: int) -> tuple[datetime, datetime]`

Get date range for last N days (including today).

**Parameters:**
- `days` - Number of days to look back

**Returns:**
- Tuple of (start_datetime, end_datetime)

#### `month_range(year: int, month: int) -> tuple[datetime, datetime]`

Get date range for a specific month.

**Parameters:**
- `year` - Year (e.g., 2024)
- `month` - Month (1-12)

**Returns:**
- Tuple of (start_datetime, end_datetime)

**Note:** Week starts on Monday (ISO 8601 standard).

### 10. Utils Module (`report/utils/categorizer.py`)

**Purpose:** Categorizes commits by component type (Console/Server/Others)

**Data Structures:**

#### `ComponentType` (Literal)

Type alias for component categories: `Literal["Console", "Server", "Others"]`

**Functions:**

#### `categorize_commit(message: str) -> ComponentType`

Categorizes a single commit message into Console, Server, or Others based on keywords.

**Parameters:**
- `message` - Commit message to categorize

**Returns:**
- ComponentType ("Console", "Server", or "Others")

**Categorization Rules:**
- **Console**: Contains keywords like "console", "ui-block", "frontend", "react", "component", "button", "modal", "page", "view", "style", "css", etc.
- **Server**: Contains keywords like "server", "nest-core", "backend", "api", "endpoint", "controller", "service", "database", "db", "query", etc.
- **Others**: Default category for commits that don't match Console or Server keywords

#### `group_commits_by_component(commits: list[str]) -> dict[ComponentType, list[str]]`

Groups a list of commits by their component type.

**Parameters:**
- `commits` - List of commit messages

**Returns:**
- Dictionary with keys "Console", "Server", "Others" and lists of commits for each

### 11. Utils Module (`report/utils/config.py`)

**Purpose:** Configuration management for report-bot

**Data Structures:**

#### `DEFAULT_CONFIG` (dict)

Default configuration structure:
- `team` - Team configuration (name, members, aliases)
- `defaults` - Default options (author, summarize, format)
- `categorization` - Component categorization keywords
- `tickets` - Custom ticket patterns

**Functions:**

#### `get_config_path() -> Path`

Get path to config file with priority order:
1. `.report-bot.json` in current directory
2. `~/.config/report-bot/config.json`
3. `~/.report-bot.json`

#### `load_config() -> dict[str, Any]`

Load configuration from file (or return defaults if not found).

#### `save_config(config: dict[str, Any]) -> None`

Save configuration to file.

#### `init_config() -> None`

Initialize config file with defaults (prompts before overwriting).

#### `get_team_members() -> list[str]`

Get team members from config.

#### `get_author_alias(author: str) -> str`

Resolve author alias from config.

#### `get_default_options() -> dict[str, Any]`

Get default options from config.

### 12. Utils Module (`report/utils/exporters.py`)

**Purpose:** Export report data to various formats

**Data Structures:**

#### `ExportFormat` (Literal)

Type alias for export formats: `Literal["json", "markdown", "html", "email"]`

**Functions:**

#### `export_to_json(commits_info: list[CommitInfo], metadata: dict | None = None) -> str`

Export commits to JSON format with metadata and timestamp.

**Returns:** JSON string

#### `export_to_markdown(commits_info: list[CommitInfo], metadata: dict | None = None, grouped: dict[str, list[CommitInfo]] | None = None) -> str`

Export commits to Markdown format with tables and optional grouping.

**Returns:** Markdown string

#### `export_to_html(commits_info: list[CommitInfo], metadata: dict | None = None, grouped: dict[str, list[CommitInfo]] | None = None) -> str`

Export commits to standalone HTML format with CSS styling.

**Returns:** HTML string

#### `export_to_email(commits_info: list[CommitInfo], metadata: dict | None = None, grouped: dict[str, list[CommitInfo]] | None = None) -> str`

Export commits to email-friendly HTML format (inline styles).

**Returns:** Email-ready HTML string

#### `export_commits(commits_info: list[CommitInfo], format: ExportFormat, metadata: dict | None = None, grouped: dict[str, list[CommitInfo]] | None = None) -> str`

Main export function that dispatches to specific exporters.

**Features:**
- Multiple output formats (JSON, Markdown, HTML, Email)
- Beautiful styling for HTML formats
- Metadata support (title, date range, author, team members)
- Grouping support (by component or author)
- Professional formatting ready for stakeholders

### 13. Utils Module (`report/utils/stats.py`)

**Purpose:** Git statistics and analytics

**Data Structures:**

#### `AuthorStats` (NamedTuple)

Statistics for a single author:
- `author: str` - Author name
- `total_commits: int` - Number of commits
- `files_changed: int` - Number of unique files modified
- `insertions: int` - Lines added
- `deletions: int` - Lines deleted
- `net_lines: int` - Net lines changed (insertions - deletions)

#### `RepoStats` (NamedTuple)

Overall repository statistics:
- `total_commits: int` - Total number of commits
- `total_authors: int` - Number of unique contributors
- `total_files_changed: int` - Total unique files modified
- `total_insertions: int` - Total lines added
- `total_deletions: int` - Total lines deleted
- `net_lines: int` - Net lines changed
- `author_stats: list[AuthorStats]` - Per-author statistics

**Functions:**

#### `get_commit_stats(repo_path: str, since: datetime, until: datetime, author: str | None = None) -> RepoStats`

Get detailed statistics for commits in a date range.

**Parameters:**
- `repo_path` - Path to git repository
- `since` - Start datetime
- `until` - End datetime
- `author` - Optional author filter

**Returns:**
- RepoStats with comprehensive statistics

**Features:**
- Analyzes git diffs to count lines changed
- Tracks files modified by each author
- Calculates net impact (additions - deletions)
- Sorts authors by commit count
- Handles both bytes and string diffs

### 14. Utils Module (`report/utils/tickets.py`)

**Purpose:** Extract and group commits by ticket/issue numbers

**Data Structures:**

#### `TicketCommits` (NamedTuple)

Commits grouped by ticket:
- `ticket_id: str` - Ticket/issue identifier
- `commits: list[CommitInfo]` - Commits for this ticket

**Functions:**

#### `extract_ticket_from_message(message: str, patterns: list[str] | None = None) -> str | None`

Extract ticket/issue number from commit message.

**Supported Patterns:**
- JIRA: `PROJECT-123`
- GitHub: `#123`, `GH-123`
- Linear: `LIN-123`
- Generic: `ticket #123`, `issue: 123`

**Returns:** Ticket ID if found, None otherwise

#### `group_commits_by_ticket(commits_info: list[CommitInfo], patterns: list[str] | None = None) -> tuple[list[TicketCommits], list[CommitInfo]]`

Group commits by ticket/issue number.

**Returns:**
- Tuple of (grouped_commits, unmatched_commits)
- grouped_commits: List of TicketCommits sorted by ticket ID
- unmatched_commits: Commits without ticket numbers

#### `format_ticket_summary(ticket_commits: list[TicketCommits]) -> str`

Format ticket summary for display.

**Features:**
- Regex-based pattern matching
- Support for multiple issue tracker formats
- Custom pattern support
- Automatic ticket ID normalization (uppercase)
- Grouped and ungrouped commit separation

### 15. AI Module (`report/ai/summarizer.py`)

**Purpose:** AI-powered commit summarization using Groq API

**Class: AICommitSummarizer**

Summarizes git commits using Groq's LLM API (llama-3.3-70b-versatile model).

**Constructor:**
```python
__init__(api_key: Optional[str] = None, verify_ssl: Optional[bool] = None)
```

**Parameters:**
- `api_key` - Groq API key (defaults to GROQ_API_KEY environment variable)
- `verify_ssl` - Whether to verify SSL certificates (defaults to GROQ_VERIFY_SSL env var, or True)

**Methods:**

#### `summarize(commits: list[str], report_type: str = "daily", grouped: dict[str, list[str]] | None = None) -> str`

Summarizes a list of commit messages into a concise, professional report.

**Parameters:**
- `commits` - List of commit messages to summarize
- `report_type` - Type of report ("daily" or "weekly")
- `grouped` - Optional dictionary of commits grouped by component (Console/Server/Others)

**Returns:**
- Summarized report text in markdown format

**Features:**
- Uses Groq API with llama-3.3-70b-versatile model (fast and free)
- Supports both ungrouped and component-grouped summarization
- For grouped commits: maintains Console/Server/Others structure
- For ungrouped commits: organizes by categories (Features, Bug Fixes, Improvements, etc.)
- Configurable SSL verification (can be disabled via GROQ_VERIFY_SSL=false in .env)
- Comprehensive error handling for SSL errors and API issues
- 30-second timeout for API calls
- Maximum 1500 tokens for response

**Environment Variables:**
- `GROQ_API_KEY` - Required: API key for Groq service
- `GROQ_VERIFY_SSL` - Optional: Set to "false" to disable SSL verification (not recommended for production)

**Error Handling:**
- Raises `ValueError` if GROQ_API_KEY is not set
- Returns helpful error messages for SSL certificate errors with fix suggestions
- Returns error messages for API request failures

## Dependencies

### Production Dependencies
- `typer` - Modern CLI framework with type hints
- `gitpython` - Python library for interacting with Git repositories
- `requests` - HTTP library for API calls (used by AI summarizer)
- `python-dotenv` - Environment variable management (used by AI summarizer)

### Additional Runtime Dependencies
- `urllib3` - HTTP library (used for SSL warning suppression)

## Development Environment

### Nix + direnv Setup

The project uses Nix and direnv for reproducible development environments:

**Nix Configuration (`shell.nix`):**
- Python 3.12
- pip and virtualenv

**direnv Configuration (`.envrc`):**
- Automatically creates Python virtual environment
- Auto-installs dependencies when `requirements.txt` changes
- Adds `bin/` directory to PATH

### Prerequisites
- Nix package manager
- direnv
- nix-direnv plugin

## Installation

### Local Development
```bash
# Dependencies are auto-installed via direnv
cd /path/to/project
direnv allow
```

### Global Installation
```bash
pipx install -e .
```

## Usage

After installation, use the `report` command:

### Basic Commands

```bash
# Generate daily report
report daily

# Generate yesterday's report  
report yesterday

# Generate weekly report
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
```

### AI Summarization

Add `--summarize` or `-s` to any command:

```bash
report daily --summarize
report weekly -s
report range --days 7 -s
```

## Technical Notes

1. **Date Handling:** All datetime operations use ISO format for git compatibility
2. **Commit Filtering:** Merge commits are excluded from reports
3. **Error Handling:** Graceful exit with helpful messages when no commits found
4. **Encoding:** Handles both UTF-8 and byte-encoded commit messages
5. **Repository Detection:** Automatically searches parent directories for git repository

## Future Improvements

Based on the current feature set, potential enhancements may include:
- Custom date range selection
- Export reports to different formats (JSON, CSV, HTML)
- Git statistics and metrics
- Multi-repository support
- Custom categorization rules

## Entry Points

**CLI Entry Point:** `report.main:main`  
**Installed Binary Name:** `report`

## Module Relationships

```
report.main
    └── imports: report.cli.app.app

report.cli.app
    ├── imports: report.cli.commands.basic
    ├── imports: report.cli.commands.advanced
    ├── imports: report.cli.commands.stats
    ├── imports: report.cli.commands.config
    └── imports: report.cli.completion

report.cli.completion
    ├── imports: os, subprocess, pathlib
    └── imports: typer

report.cli.commands.basic
    ├── imports: report.cli.formatters
    ├── imports: report.cli.handlers
    ├── imports: report.git.commits
    ├── imports: report.utils.categorizer
    └── imports: report.utils.dates

report.cli.commands.advanced
    ├── imports: report.cli.formatters
    ├── imports: report.git.commits
    ├── imports: report.utils.dates
    └── imports: report.utils.tickets

report.cli.commands.stats
    ├── imports: report.utils.dates
    └── imports: report.utils.stats

report.cli.commands.config
    └── imports: report.utils.config

report.cli.formatters
    └── imports: report.git.commits.CommitInfo

report.cli.handlers
    ├── imports: report.ai.summarizer
    ├── imports: report.cli.formatters
    ├── imports: report.git.commits
    ├── imports: report.utils.categorizer
    └── imports: report.utils.exporters

report.git.commits
    └── imports: git.Repo (from gitpython)

report.utils.dates
    └── imports: datetime (standard library)

report.utils.categorizer
    └── imports: re (standard library)

report.utils.config
    └── imports: json, pathlib (standard library)

report.utils.exporters
    └── imports: report.git.commits.CommitInfo

report.utils.stats
    ├── imports: git.Repo (from gitpython)
    └── imports: report.git.commits.CommitInfo

report.utils.tickets
    └── imports: report.git.commits.CommitInfo

report.ai.summarizer
    ├── imports: requests (HTTP library)
    ├── imports: python-dotenv (environment variables)
    └── imports: urllib3 (SSL warning suppression)
```
