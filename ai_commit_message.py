#!/usr/bin/env python3
import os
import sys
import tty
import termios
import subprocess
import tempfile
from anthropic import Anthropic
from argparse import ArgumentParser


def getch() -> str:
    """Get a single character from stdin without requiring Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_git_diff(all_changes: bool = False) -> str:
    """Get the git diff based on mode."""
    try:
        cmd = ["git", "status", "-s"]
        status = subprocess.check_output(cmd, text=True, cwd=os.getcwd())
        if not status.strip():
            return ""

        if all_changes:
            cmd = ["git", "diff", "HEAD"]
        else:
            cmd = ["git", "diff", "--cached"]

        return subprocess.check_output(cmd, text=True, cwd=os.getcwd())
    except subprocess.CalledProcessError:
        return ""


def edit_message(initial_message: str) -> str:
    """Open nvim to edit the commit message."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as tf:
        tf_name = tf.name
        tf.write(initial_message)
        tf.flush()
        os.fsync(tf.fileno())  # Force sync to disk

    try:
        subprocess.run(["nvim", tf_name], check=True)
        with open(tf_name, "r") as f:
            edited_message = f.read().strip()
        return edited_message if edited_message else initial_message
    except subprocess.CalledProcessError:
        return initial_message
    finally:
        os.unlink(tf_name)  # Clean up the temporary file


def generate_commit_message(diff: str, conventional: bool = False) -> str:
    """Generate a commit message using Claude.

    Args:
        diff: The git diff content
        conventional: Whether to use conventional commit format
    """
    if not diff:
        return ""

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    if conventional:
        prompt = (
            "Generate a single-line conventional commit message for these changes:\n\n"
            f"```diff\n{diff}\n```\n\n"
            "Rules:\n"
            "1. Message must be in this exact format: <type>: <description>\n"
            "2. Type must be one of:\n"
            "   - fix: A bug fix. Correlates with PATCH in SemVer\n"
            "   - feat: A new feature. Correlates with MINOR in SemVer\n"
            "   - docs: Documentation only changes\n"
            "   - style: Changes that do not affect the meaning of the code\n"
            "   - refactor: A code change that neither fixes a bug nor adds a feature\n"
            "   - perf: A code change that improves performance\n"
            "   - test: Adding missing or correcting existing tests\n"
            "   - build: Changes that affect the build system or external dependencies\n"
            "   - ci: Changes to CI configuration files and scripts\n"
            "3. Description must be:\n"
            "   - Written in lower case\n"
            "   - Imperative, present tense (e.g., 'add' not 'added')\n"
            "   - No period at the end\n"
            "   - Under 72 characters total\n"
            "   - A short and imperative summary of the code changes\n"
        )
        system_prompt = "You are a commit message generator that creates conventional commit messages exactly matching Commitizen's format."
    else:
        prompt = (
            "Generate a short, clear commit message for these changes:\n\n"
            f"```diff\n{diff}\n```\n\n"
            "Rules:\n"
            "1. Return ONLY the message text with no formatting, quotes, or backticks\n"
            "2. DO NOT use type prefixes (like 'fix:', 'feat:', etc.) - just write a plain message\n"
            "3. Start with a capitalized verb in imperative form (e.g., 'Add' not 'Added' or 'Adds')\n"
            "4. No period at the end\n"
            "5. Under 72 characters total\n"
            "6. Examples of good messages:\n"
            "   - Update user authentication logic\n"
            "   - Add support for dark mode\n"
            "   - Fix database connection timeout\n"
            "   NOT:\n"
            "   - `Fix database timeout` (no backticks!)\n"
            "   - fix: update user auth (no type prefixes!)\n"
            "   - Updated user authentication (use imperative!)\n"
        )
        system_prompt = "You are a commit message generator. Output ONLY the raw message text without any formatting, quotes, or backticks. For regular commits, create concise messages without type prefixes. Start with a capital verb in imperative mood."

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        temperature=0,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return str(message.content[0].text).strip()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--all", action="store_true", help="Include all changes (not just staged)"
    )
    parser.add_argument(
        "--commit", action="store_true", help="Create the commit after confirmation"
    )
    parser.add_argument(
        "-c",
        "--conventional",
        action="store_true",
        help="Use conventional commit format (type: description)",
    )
    args = parser.parse_args()

    try:
        diff = get_git_diff(args.all)
        commit_msg = generate_commit_message(diff, args.conventional)
        if not commit_msg:
            sys.exit(1)  # No changes to commit

        print(commit_msg, end="", flush=True)

        if args.commit:
            key = getch()  # Get single keypress
            print()  # Add newline after keypress

            if key.lower() == "e":
                commit_msg = edit_message(commit_msg)
            elif key != "\r":  # If not Enter, exit with error
                sys.exit(1)

            # Only reach here if 'e' or Enter was pressed
            cmd = ["git", "commit", "-m", commit_msg]
            if args.all:
                cmd.insert(2, "-a")
            # Redirect stdout and stderr to devnull to suppress git's output
            with open(os.devnull, "w") as devnull:
                try:
                    subprocess.run(
                        cmd, check=True, cwd=os.getcwd(), stdout=devnull, stderr=devnull
                    )
                    sys.exit(0)  # Only exit with 0 if commit succeeded
                except subprocess.CalledProcessError:
                    sys.exit(1)  # Exit with error if commit failed

    except KeyboardInterrupt:
        print()  # Add newline after ^C
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
