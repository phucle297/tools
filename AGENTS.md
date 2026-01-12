# AGENTS.md

## Project Overview

**Project Name:** report-bot  
**Description:** Daily & Weekly Git Report CLI tool for lazy developers  
**Version:** 0.1.0

This is a Python-based CLI tool that generates daily and weekly reports of git commits from a repository.

## Project Structure

```
.
├── report/
│   ├── __init__.py
│   ├── cli.py                 # Main CLI application entry point
│   ├── git/
│   │   ├── __init__.py
│   │   └── commits.py         # Git commit retrieval logic
│   └── utils/
│       ├── __init__.py
│       └── dates.py           # Date range utilities
├── bin/
│   └── report                 # Binary entry point
├── pyproject.toml             # Project configuration and dependencies
├── requirements.txt           # Python dependencies
├── shell.nix                  # Nix shell configuration
├── .envrc                     # direnv configuration
└── README.md                  # Project documentation
```

## Core Components

### 1. CLI Module (`report/cli.py`)

**Purpose:** Main command-line interface using Typer framework

**Commands:**
- `daily` - Generates a report of commits made today
- `weekly` - Generates a report of commits made this week (Monday-Sunday)

**Key Features:**
- User-friendly CLI with Typer
- Displays commit messages in a simple list format
- Exits gracefully when no commits are found

**Dependencies:**
- `typer` - CLI framework
- `report.git.commits.get_commits` - Commit retrieval function
- `report.utils.dates` - Date range utilities

### 2. Git Module (`report/git/commits.py`)

**Purpose:** Handles git repository operations and commit retrieval

**Functions:**

#### `get_commits(repo_path: str, since: datetime, until: datetime) -> list[str]`

Retrieves commit messages from a git repository within a specified date range.

**Parameters:**
- `repo_path` - Path to the git repository
- `since` - Start datetime for commit range
- `until` - End datetime for commit range

**Returns:**
- List of commit message strings

**Features:**
- Searches parent directories for git repository
- Filters out merge commits (`no_merges=True`)
- Handles both byte and string commit messages
- Proper error handling for non-git directories

**Error Handling:**
- Raises `RuntimeError` if not in a git repository

### 3. Utils Module (`report/utils/dates.py`)

**Purpose:** Provides date range utilities for report generation

**Functions:**

#### `today_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for today (00:00:00 to 23:59:59).

#### `this_week_range() -> tuple[datetime, datetime]`

Returns the start and end datetime for the current week (Monday 00:00:00 to Sunday 23:59:59).

**Note:** Week starts on Monday (ISO 8601 standard).

## Dependencies

### Production Dependencies
- `typer` - Modern CLI framework with type hints
- `gitpython` - Python library for interacting with Git repositories

### Development Dependencies (in requirements.txt)
- `jinja2` - Template engine (unused in current code)
- `requests` - HTTP library (unused in current code)
- `python-dotenv` - Environment variable management (unused in current code)

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

```bash
# Generate daily report
report daily

# Generate weekly report
report weekly
```

## Technical Notes

1. **Date Handling:** All datetime operations use ISO format for git compatibility
2. **Commit Filtering:** Merge commits are excluded from reports
3. **Error Handling:** Graceful exit with helpful messages when no commits found
4. **Encoding:** Handles both UTF-8 and byte-encoded commit messages
5. **Repository Detection:** Automatically searches parent directories for git repository

## Future Improvements

Based on unused dependencies in `requirements.txt`, potential planned features may include:
- Template-based report formatting (Jinja2)
- Remote API integration (requests)
- Configuration management via environment variables (python-dotenv)

## Entry Points

**CLI Entry Point:** `report.cli:main`  
**Installed Binary Name:** `report`

## Module Relationships

```
report.cli
    ├── imports: report.git.commits.get_commits
    ├── imports: report.utils.dates.today_range
    └── imports: report.utils.dates.this_week_range

report.git.commits
    └── imports: git.Repo (from gitpython)

report.utils.dates
    └── imports: datetime (standard library)
```
