# AGENTS.md

## Project Overview

**Project Name:** toolkit  
**Description:** A comprehensive toolkit of standalone CLI tools for developers  
**Version:** 0.3.0

A collection of Python-based CLI tools:
- `report` - Daily & Weekly Git Report CLI
- `review` - Code review helper
- `benchmark` - Performance benchmark CLI
- `translate` - i18n helper
- `port` - Port conflict resolver

## Project Structure

```
.
├── bin/                      # CLI entry points
│   ├── report
│   ├── review
│   ├── benchmark
│   ├── translate
│   └── port
├── report/                   # Git Report CLI
│   ├── __init__.py
│   ├── main.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── completion.py
│   │   ├── formatters.py
│   │   ├── handlers.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── basic.py
│   │       ├── advanced.py
│   │       ├── stats.py
│   │       └── config.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── summarizer.py
│   ├── git/
│   │   ├── __init__.py
│   │   └── commits.py
│   └── utils/
│       ├── __init__.py
│       ├── categorizer.py
│       ├── config.py
│       ├── dates.py
│       ├── exporters.py
│       ├── stats.py
│       └── tickets.py
├── review/                   # Code Review Helper
│   ├── __init__.py
│   └── main.py
├── benchmark/                # Performance Benchmark
│   ├── __init__.py
│   └── main.py
├── translate/                # i18n Helper
│   ├── __init__.py
│   └── main.py
├── port/                     # Port Conflict Resolver
│   ├── __init__.py
│   └── main.py
├── tools/                    # Toolkit Manager
│   ├── __init__.py
│   └── main.py               # 'tools list' and 'tools completion' commands
├── shared/                   # Shared Utilities
│   ├── __init__.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── summarizer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── categorizer.py
│   └── dates.py
├── tests/
├── pyproject.toml
├── requirements.txt
├── TODO.md
├── README.md
└── AGENTS.md
```

## Shared Utilities (`shared/`)

### `shared/dates.py`

Date range utilities for reports:
- `today_range()` - Today's date range
- `yesterday_range()` - Yesterday's date range
- `this_week_range()` - Current week's date range
- `last_week_range()` - Last week's date range
- `custom_range(from_date, to_date)` - Custom date range
- `last_n_days_range(days)` - Last N days
- `month_range(year, month)` - Specific month

### `shared/ai/summarizer.py`

AI-powered commit summarization using Groq API:
- Uses `llama-3.3-70b-versatile` model
- Requires `GROQ_API_KEY` environment variable
- Supports grouped and non-grouped commits
- 30-second timeout, 1500 max tokens

### `shared/utils/categorizer.py`

Commit categorization by component:
- `categorize_commit(message)` - Categorize as Console/Server/Others
- `group_commits_by_component(commits)` - Group commits by component
- `ComponentType` - Literal type alias

### `shared/completion.py`

Shell completion utilities for all toolkit commands:
- `install_all_bash_completion()` - Install bash completion
- `install_all_zsh_completion()` - Install zsh completion
- `install_all_fish_completion()` - Install fish completion
- `show_bash_completion()` - Show bash completion script
- `show_zsh_completion()` - Show zsh completion script
- `show_fish_completion()` - Show fish completion script
- `TOOLS` - List of all toolkit commands

## Tool Entry Points

| Tool | Entry Point | Binary |
|------|-------------|--------|
| report | `report.main:main` | `report` |
| commit | `commit.main:main` | `commit` |
| review | `review.main:main` | `review` |
| benchmark | `benchmark.main:main` | `benchmark` |
| mock | `mock.main:main` | `mock` |
| translate | `translate.main:main` | `translate` |
| port | `port.main:main` | `port` |
| tools | `tools.main:main` | `tools` |

## Shell Completion

Install completion for all toolkit commands (including `tools` itself):

```bash
# Auto-detect shell and install
tools completion

# Specify shell explicitly
tools completion --shell bash
tools completion --shell zsh
tools completion --shell fish
```

### Generated Files

**Fish:** `~/.config/fish/completions/{report,review,benchmark,translate,port,tools}.fish`

**Bash:** `~/.bash_completions/{toolkit.sh,tools.sh}`

**Zsh:** `~/.zsh/completions/_{report,review,benchmark,translate,port,tools}`

## Dependencies

- `typer` - CLI framework
- `gitpython` - Git operations
- `requests` - HTTP library
- `python-dotenv` - Environment variables
- `urllib3` - SSL warning suppression

## Development

```bash
# Install
pipx install -e .

# Reinstall after changes
pipx uninstall toolkit && pipx install -e .
```

## Module Relationships

```
shared/
├── shared.dates
├── shared.ai.summarizer
└── shared.utils.categorizer

report/
├── report.main → report.cli.app
├── report.cli.app → report.cli.commands.*
├── report.cli.commands.* → report.cli.formatters, report.cli.handlers
├── report.cli.handlers → report.ai.summarizer, report.cli.formatters
└── report.utils.* → shared.dates, shared.utils.categorizer

review/
├── review.main → review.cli
└── review.cli → shared.ai.summarizer

review/main.py
benchmark/main.py
translate/main.py
port/main.py
tools/main.py → shared/completion.py → install_all_{bash,zsh,fish}_completion()
```

## Adding New Tools

Follow the pattern of existing tools:

1. Create directory `toolname/`
2. Create `toolname/__init__.py`
3. Create `toolname/main.py` with Typer app
4. Create `toolname/cli.py` (if complex)
5. Add entry point to `pyproject.toml`
6. Add bin script in `bin/toolname`
7. Import shared utilities where possible
