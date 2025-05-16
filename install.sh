#!/bin/bash
set -e

# Get the absolute path to the repository
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for sudo permissions when linking to /usr/local/bin
if [ ! -w /usr/local/bin ]; then
    echo "This script needs sudo permissions to create symlinks in /usr/local/bin"
    echo "Please run with sudo: sudo ./install.sh"
    exit 1
fi

# Install Python dependencies and package
echo "Installing git-ai-commit with Poetry..."
(cd "$SCRIPT_DIR" && poetry install)

# Check if gcai and gcamai are available in the PATH
if ! command -v gcai &>/dev/null || ! command -v gcamai &>/dev/null; then
    echo "Creating symlinks for commands in /usr/local/bin..."
    
    # Get the paths to the entry points
    GCAI_PATH=$(poetry run which gcai 2>/dev/null || echo "")
    GCAMAI_PATH=$(poetry run which gcamai 2>/dev/null || echo "")
    
    if [ -n "$GCAI_PATH" ] && [ -n "$GCAMAI_PATH" ]; then
        ln -sf "$GCAI_PATH" /usr/local/bin/gcai
        ln -sf "$GCAMAI_PATH" /usr/local/bin/gcamai
    else
        echo "ERROR: Could not find gcai and gcamai entry points after installation."
        echo "Please check your Poetry installation and try again."
        exit 1
    fi
fi

# Check for ANTHROPIC_API_KEY in environment
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "NOTE: You need to set the ANTHROPIC_API_KEY environment variable."
    echo "Add the following line to your ~/.bashrc, ~/.zshrc, or equivalent shell config file:"
    echo ""
    echo "  export ANTHROPIC_API_KEY=your_api_key_here"
    echo ""
fi

echo "Installation complete! You can now use 'gcai' and 'gcamai' commands from anywhere."