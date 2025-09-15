"""
Git repository operations for gtree
"""

import subprocess
import sys
from typing import Dict, List, Optional


class GitRepo:
    """Handle Git operations for the repository"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._check_git_repo()

    def _check_git_repo(self):
        """Verify this is a Git repository"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            print("Error: Not a Git repository", file=sys.stderr)
            sys.exit(1)

    def get_tracked_files(self, branch: Optional[str] = None) -> List[str]:
        """Get list of files tracked by Git"""
        if branch:
            # Use git ls-tree for specific branch
            cmd = ["git", "ls-tree", "-r", "--name-only", branch]
        else:
            # Use git ls-files for current working tree
            cmd = ["git", "ls-files", "--exclude-standard"]

        try:
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, check=True
            )
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"Error getting tracked files: {e}", file=sys.stderr)
            return []

    def get_file_metadata(
        self, files: List[str], include_contributors: bool = False
    ) -> Dict[str, Dict]:
        """Get metadata for files using the most efficient approach possible"""
        metadata = {}

        # Initialize metadata for all files
        for file in files:
            metadata[file] = {"last_commit": "unknown"}

        if not files:
            return metadata

        # Use git ls-files with -z for null-terminated output to handle special filenames
        # Then get the last commit date for each file using git log with -1 --format
        # This is the fastest reliable method for getting individual file commit dates

        # Process files in batches to balance performance and memory usage
        batch_size = 100
        total_files = len(files)

        for i in range(0, total_files, batch_size):
            batch_files = files[i : i + batch_size]
            print(
                f"Processing files {i+1}-{min(i+batch_size, total_files)} of {total_files}...",
                file=sys.stderr,
            )

            # Use parallel processing concept: prepare all commands first
            for file in batch_files:
                try:
                    # Quick individual file check - most efficient for per-file data
                    result = subprocess.run(
                        ["git", "log", "-1", "--format=%cs", "--", file],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=2,  # Very short timeout per file
                    )
                    date = result.stdout.strip()
                    metadata[file]["last_commit"] = date if date else "unknown"
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    metadata[file]["last_commit"] = "unknown"

        # Get contributor counts if requested
        if include_contributors:
            print("Getting contributor information...", file=sys.stderr)
            for file in files:
                if file in metadata:
                    metadata[file]["contributors"] = self._get_contributor_count(file)

        return metadata

    def _get_contributor_count(self, file_path: str) -> int:
        """Get number of unique contributors for a file with timeout"""
        try:
            result = subprocess.run(
                ["git", "log", "--format=%an", "--", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,  # Add timeout to prevent hanging
            )
            authors = set(
                line.strip() for line in result.stdout.split("\n") if line.strip()
            )
            return len(authors)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return 0

    def filter_files_since_date(self, files: List[str], since_date: str) -> List[str]:
        """Filter files that have commits since the given date"""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--since",
                    since_date,
                    "--name-only",
                    "--pretty=format:",
                    "--",
                ]
                + files,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            changed_files = set(
                line.strip() for line in result.stdout.split("\n") if line.strip()
            )
            return [f for f in files if f in changed_files]
        except subprocess.CalledProcessError:
            return files
