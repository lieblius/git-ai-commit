#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
import subprocess

from git_ai_commit.core import get_git_diff, generate_commit_message, getch, edit_message


def main(all_changes=False, commit=True, conventional=False) -> int:
    """Main entry point for the CLI."""
    try:
        diff = get_git_diff(all_changes)
        commit_msg = generate_commit_message(diff, conventional)
        if not commit_msg:
            return 1  # No changes to commit

        print(commit_msg, end="", flush=True)

        if commit:
            key = getch()  # Get single keypress
            print()  # Add newline after keypress

            if key.lower() == "e":
                commit_msg = edit_message(commit_msg)
            elif key != "\r":  # If not Enter, exit with error
                return 1

            # Only reach here if 'e' or Enter was pressed
            cmd = ["git", "commit", "-m", commit_msg]
            if all_changes:
                cmd.insert(2, "-a")
            # Redirect stdout and stderr to devnull to suppress git's output
            with open(os.devnull, "w") as devnull:
                try:
                    subprocess.run(
                        cmd, check=True, cwd=os.getcwd(), stdout=devnull, stderr=devnull
                    )
                    # Print the commit hash
                    hash_cmd = ["git", "--no-pager", "log", "-1", "--pretty=format:%h"]
                    subprocess.run(hash_cmd, check=True, cwd=os.getcwd())
                    return 0  # Only exit with 0 if commit succeeded
                except subprocess.CalledProcessError:
                    return 1  # Exit with error if commit failed
        return 0

    except KeyboardInterrupt:
        print()  # Add newline after ^C
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def parse_args():
    """Parse command line arguments."""
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
    return parser.parse_args()


def run_staged():
    """Entry point for gcai command (staged changes only)."""
    args = parse_args()
    args.commit = True if args.commit is None else args.commit
    return main(all_changes=False, commit=args.commit, conventional=args.conventional)


def run_all():
    """Entry point for gcamai command (all changes)."""
    args = parse_args()
    args.all = True
    args.commit = True if args.commit is None else args.commit
    return main(all_changes=True, commit=args.commit, conventional=args.conventional)


if __name__ == "__main__":
    sys.exit(main())