# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

git-ai-commit is a Python-based tool that generates AI-powered commit messages for git repositories using the Anthropic Claude API. The tool analyzes git diffs and creates informative commit messages that match best practices.

## Setup and Installation

```bash
# Install dependencies with Poetry
poetry install

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_api_key_here
```

## Commands

### Running the Tool

There are two main script entry points:

```bash
# Generate commit message for staged changes
./gcai [--conventional|-c]

# Generate commit message for all changes (staged and unstaged)
./gcamai [--conventional|-c]
```

The `--conventional` or `-c` flag can be added to generate messages in conventional commit format (e.g., "feat: add user authentication").

### Development Commands

```bash
# Run tests
poetry run pytest

# Run linting
poetry run flake8

# Format code
poetry run black .
```

## Architecture

The project has a simple structure:

1. `ai_commit_message.py` - Main Python module containing all functionality:
   - `get_git_diff()` - Retrieves git diff content
   - `generate_commit_message()` - Uses Claude API to generate commit messages
   - `edit_message()` - Opens nvim for manual editing of messages
   - `main()` - Entry point with command-line argument parsing

2. Command-line entry points:
   - `gcai` - Generates commit messages for staged changes
   - `gcamai` - Generates commit messages for all changes (staged + unstaged)

## Requirements

- Python 3.11+
- Poetry for dependency management
- Git
- Anthropic API key
- nvim (for editing commit messages)

## Important Implementation Notes

1. The tool uses the Anthropic Claude API (claude-3-5-sonnet model) to generate commit messages
2. Supports two message formats:
   - Standard commit messages (capitalized, imperative form)
   - Conventional commit format (type: description)
3. When run with the `--commit` flag (default in the scripts), it will:
   - Display the suggested commit message
   - Wait for user input:
     - Press Enter to accept and commit
     - Press 'e' to edit the message in nvim
     - Press any other key to cancel