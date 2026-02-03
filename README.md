# Toolkit - Developer CLI Tools

A comprehensive toolkit of standalone CLI tools for developers.

## Tools

| Tool | Description |
|------|-------------|
| `report` | Daily & Weekly Git Report CLI |
| `review` | Code review helper |
| `benchmark` | Performance benchmark CLI |
| `translate` | i18n helper |
| `port` | Port conflict resolver |
| `tools` | Toolkit manager (list commands, install completion) |

## Installation

```bash
pipx install -e .
```

## tools - Toolkit Manager

Manage toolkit commands and install shell completion.

### Usage

```bash
# List all available commands
tools list

# Install shell completion for all tools (including tools itself)
tools completion
tools completion --shell bash
tools completion --shell zsh
tools completion --shell fish
```

---

## Shared Utilities

All tools use shared utilities from `shared/`:
- `shared/dates.py` - Date range utilities
- `shared/ai/` - AI summarizer (Groq API)
- `shared/utils/` - Utilities (categorizer, etc.)

---

## report - Git Report CLI

Generate beautiful git commit reports with AI-powered summarization.

### Usage

```bash
# Basic reports
report daily
report yesterday
report weekly
report lastweek

# Custom date range
report range --days 7
report range --from 2024-01-01 --to 2024-01-31
report range --month 12 --year 2024

# Team reports
report daily --team
report weekly --team --author "John Doe"

# AI summarization
report daily --summarize
report weekly -s

# Statistics
report stats
report stats weekly
report compare thisweek lastweek

# Advanced
report filter --days 7 --include "feat,fix"
report search "bug" --days 30
report tickets --days 7
```

### Options

- `--summarize, -s`: Add AI summary
- `--author, -a NAME`: Filter by author
- `--team, -t`: Show all team members
- `--export FORMAT`: Export to json/markdown/html/email

---

## review - Code Review Helper

Review code changes efficiently.

### Usage

```bash
# Review staged changes
review diff
review diff --ai  # AI summary
review diff --verbose  # Full diff

# Review specific commit
review commit abc1234
review commit abc1234 --ai

# Statistics
review stats
review stats --from 2024-01-01 --to 2024-01-31
```

### Options

- `--ai, -a`: Generate AI review summary
- `--verbose, -v`: Show full diff

---

## benchmark - Performance Benchmark CLI

Measure and compare performance metrics.

### Usage

```bash
# Run benchmark
benchmark run mybench -c "python script.py" --iterations 5

# Compare results
benchmark compare mybench1 mybench2

# Show history
benchmark history

# Clear history
benchmark clear
```

### Options

- `-c, --command`: Command to benchmark
- `-n, --iterations`: Number of iterations (default: 3)
- `--save/--no-save`: Save result for comparison

---

## translate - i18n Helper

Manage and translate i18n resource files.

### Usage

```bash
# Check for missing keys
translate check ./locales
translate check ./locales --reference en

# Export missing keys
translate missing ./locales -o missing.json

# Show statistics
translate stats ./locales
```

### Options

- `-r, --reference`: Reference language code (default: en)
- `-o, --output`: Output file for missing keys

---

## port - Port Conflict Resolver

Detect and resolve port conflicts.

### Usage

```bash
# List all used ports
port list

# Check specific port
port list --port 8080

# Find process on port
port find 8080
port find 8080 --kill  # Kill the process

# Find free port
port free --start 8000 --end 9000
```

### Options

- `-p, --port`: Check specific port
- `-k, --kill`: Kill the process
- `-s, --start`: Start of port range
- `-e, --end`: End of port range

---

## AI Summarization (Optional)

To use AI-powered features, set up a Groq API key:

1. Get a free API key from: https://console.groq.com/keys
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_api_key_here
   ```

---

## Shell Completion

Install shell completion for **all** toolkit commands (including `tools` itself) with a single command:

```bash
# Install completion (auto-detects your shell)
tools completion

# Install for specific shell
tools completion --shell bash
tools completion --shell zsh
tools completion --shell fish
```

After installation, restart your terminal or run:

```bash
# Bash
source ~/.bashrc

# Fish
source ~/.config/fish/config.fish

# Zsh
source ~/.zshrc
```

### What gets installed

| Shell | Files Created |
|-------|---------------|
| Fish | `~/.config/fish/completions/{report,review,benchmark,translate,port,tools}.fish` |
| Bash | `~/.bash_completions/{toolkit.sh,tools.sh}` |
| Zsh | `~/.zsh/completions/_{report,review,benchmark,translate,port,tools}` |

---

## Project Structure

```
.
├── bin/                    # CLI entry points
│   ├── report
│   ├── review
│   ├── benchmark
│   ├── translate
│   └── port
├── report/                 # Report CLI
├── review/                 # Code review helper
├── benchmark/              # Performance benchmark
├── translate/              # i18n helper
├── port/                   # Port conflict resolver
├── tools/                  # Toolkit manager (list, completion)
├── shared/                 # Shared utilities
│   ├── ai/                 # AI summarizer
│   ├── utils/              # Utilities
│   ├── dates.py            # Date utilities
│   └── completion.py       # Shell completion installer
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

---

## Development

```bash
# Install dependencies
pip install -e .

# Reinstall after changes
pipx uninstall toolkit && pipx install -e .
```
