# git-ai-commit

AI-powered git commit message generator using the Anthropic Claude API. This tool analyzes git diffs and creates informative commit messages that match best practices.

## Features

- Generate concise, clear commit messages for your git changes
- Supports both standard and conventional commit formats
- Interactive mode for editing or accepting the suggested message
- Works with either staged changes only or all modified files

## Installation

### From Source with pip

```bash
# Clone the repository
git clone https://github.com/lieblius/git-ai-commit.git
cd git-ai-commit

# Install with Poetry
poetry install

# Or with pip
pip install .
```

### Using Homebrew (coming soon)

```bash
brew install lieblius/tools/git-ai-commit
```

## Usage

Before using, set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### Commands

```bash
# Generate commit message for staged changes
gcai [--conventional|-c]

# Generate commit message for all changes (staged and unstaged)
gcamai [--conventional|-c]
```

### Options

- `--conventional` or `-c`: Use conventional commit format (e.g., "feat: add user authentication")
- Both commands run in interactive mode by default, prompting you to:
  - Press Enter to accept and commit
  - Press 'e' to edit the message in nvim
  - Press any other key to cancel

## Requirements

- Python 3.11+
- Git
- Anthropic API key
- nvim (for editing commit messages)

## License

MIT