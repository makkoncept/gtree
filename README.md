# gtree

A Git-aware directory tree utility that displays your repository structure while respecting `.gitignore` and enriching files with lightweight Git metadata. Built with zero external dependencies for maximum portability and minimal setup.

## Features

- **Fast performance** - Uses efficient Git commands, no expensive operations
- **Auto-fast mode** - Automatically skips metadata for repositories with >1000 files
- **Fast mode** - Optional `--fast` flag to skip metadata entirely for maximum speed
- **Recency heatmap** - Color-codes based on last commit date
- **Contributor tracking** - Optional display of unique contributor counts
- **Flexible filtering** - Filter by branch, date, or file extension
- **JSON output** - Machine-readable output option

## Installation

### From source
```bash
git clone https://github.com/makkoncept/gtree.git
cd gtree
chmod +x gtree_cli.py
./gtree_cli.py --help
```

### As a Python package
```bash
pip install -e .
```

> **Note**: If you encounter "Multiple .egg-info directories found" errors, clean up any build artifacts first:
> ```bash
> rm -rf *.egg-info/ build/ dist/
> ```

## Usage

### Basic usage

> **Note**: Assuming installation as a python package

```bash
# Show tree for current repository
gtree

# Fast mode (no metadata, much faster for large repos)
gtree --fast

# Show tree with contributor counts
gtree --contributors

# Show tree for specific branch
gtree --branch feature_branch

# Filter files modified since date
gtree --since "2023-01-01"

# Filter by extension (eg: show only Python files)
gtree --ext py

# JSON output
gtree --json

# Disable colors
gtree --no-color

# Set custom limit for auto-fast mode (default: 1000 files)
gtree --limit 2000
```

## Color coding

Files are color-coded based on recency of last commit:
- **Red**: Last 7 days (most recent)
- **Orange**: Last 30 days  
- **Yellow**: Last 90 days
- **Green**: Older than 90 days

> **Note**: Colors are visible in terminal output but not shown in the above examples. Use `--no-color` to disable colored output.

## Requirements

- Python 3.7+
- No other dependency

## CLI Options

| Option | Description |
|--------|-------------|
| `--contributors` | Show number of unique contributors per file |
| `--branch <name>` | Show tree for specific branch |
| `--since <date>` | Filter files with commits since given date |
| `--ext <extension>` | Show only files with given extension |
| `--json` | Output machine-readable JSON |
| `--no-color` | Disable color output |
| `--fast` | Fast mode: skip metadata (instant for large repos) |
| `--limit <number>` | Auto-fast threshold (default: 1000 files) |

## Performance Notes

gtree is designed to be fast by:
- Using `git ls-files --exclude-standard` instead of filesystem scanning
- Auto-fast mode: Automatically skips metadata for repositories with >1000 files
- Fast mode: Use `--fast` to skip metadata entirely for maximum speed
- Smart thresholds: Configurable auto-fast threshold via `--limit` (default: 1000)
- Batching Git commands where possible
- Adding timeouts to prevent hanging on large repositories
- Avoiding expensive operations like `git blame` or full diff parsing

### Performance Examples
- **Small repos** (< 100 files): ~0.1-0.5 seconds with full metadata
- **Medium repos** (100-1000 files): ~0.5-2 seconds with full metadata  
- **Large repos** (> 1000 files): ~0.1-0.2 seconds in auto-fast mode
- **Very large repos**: Use `--fast` for instant results (~0.05-0.1 seconds)
