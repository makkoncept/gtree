"""
Command-line interface for gtree
"""

import argparse
import json
import sys

from .git_repo import GitRepo
from .tree_renderer import TreeRenderer


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Git-aware directory tree utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--contributors",
        action="store_true",
        help="Show number of unique contributors per file",
    )

    parser.add_argument("--branch", type=str, help="Show tree for specific branch")

    parser.add_argument(
        "--since",
        type=str,
        help="Filter files with commits since given date (e.g., '2023-01-01')",
    )

    parser.add_argument(
        "--ext", type=str, help="Show only files with given extension (e.g., 'py')"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of text tree",
    )

    parser.add_argument("--no-color", action="store_true", help="Disable color output")

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Git repository (default: current directory)",
    )

    return parser


def main():
    """Main entry point for gtree CLI"""
    parser = create_parser()
    args = parser.parse_args()

    repo = GitRepo(args.path)

    # Get tracked files
    files = repo.get_tracked_files(args.branch)

    if not files:
        print("No tracked files found", file=sys.stderr)
        sys.exit(1)

    # Apply filters
    if args.since:
        files = repo.filter_files_since_date(files, args.since)

    if args.ext:
        files = [f for f in files if f.endswith(f".{args.ext}")]

    if not files:
        print("No files match the specified criteria", file=sys.stderr)
        sys.exit(1)

    metadata = repo.get_file_metadata(files, args.contributors)

    if args.json:
        # JSON output
        result = {
            "files": [
                {"path": file_path, **metadata.get(file_path, {})}
                for file_path in files
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        # Tree output
        renderer = TreeRenderer(use_colors=not args.no_color)
        tree_output = renderer.render_tree(files, metadata, args.contributors)
        print(tree_output)


if __name__ == "__main__":
    main()
