"""
Tree rendering functionality for gtree
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .colors import Colors


class TreeRenderer:
    """Render directory tree structure"""

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

    def get_recency_color(self, date_str: str) -> str:
        """Get color based on commit recency"""
        if not self.use_colors or date_str == "unknown":
            return ""

        try:
            commit_date = datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.now()
            days_ago = (now - commit_date).days

            if days_ago <= 7:
                return Colors.RED
            elif days_ago <= 30:
                return Colors.ORANGE
            elif days_ago <= 90:
                return Colors.YELLOW
            else:
                return Colors.GREEN
        except ValueError:
            return ""

    def build_tree_structure(self, files: List[str]) -> Dict:
        """Build nested tree structure from file list"""
        tree = {}

        for file_path in files:
            parts = Path(file_path).parts
            current = tree

            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {}

                if i == len(parts) - 1:
                    # file (leaf node)
                    current[part]["__is_file__"] = True
                    current[part]["__path__"] = file_path
                else:
                    # directory
                    current = current[part]

        return tree

    def render_tree(
        self,
        files: List[str],
        metadata: Dict[str, Dict],
        include_contributors: bool = False,
    ) -> str:
        """Render the tree structure as text"""
        tree = self.build_tree_structure(files)
        lines = []

        def render_node(node: Dict, name: str, prefix: str = "", is_last: bool = True):
            if "__is_file__" in node:
                # Processing for file
                file_path = node["__path__"]
                file_meta = metadata.get(file_path, {})

                # Build file info
                info_parts = []
                if "last_commit" in file_meta:
                    date_str = file_meta["last_commit"]
                    color = self.get_recency_color(date_str)
                    reset = Colors.RESET if color else ""
                    info_parts.append(f"{color}[{date_str}]{reset}")

                if include_contributors and "contributors" in file_meta:
                    count = file_meta["contributors"]
                    plural = "author" if count == 1 else "authors"
                    info_parts.append(f"({count} {plural})")

                info = " " + " ".join(info_parts) if info_parts else ""

                # Tree connector
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{name}{info}")
            else:
                # Processing for directory
                if name:  # Don't print root
                    connector = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{connector}{name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                else:
                    new_prefix = prefix

                # Sort children: directories first, then files
                children = [(k, v) for k, v in node.items() if not k.startswith("__")]
                dirs = [(k, v) for k, v in children if "__is_file__" not in v]
                files = [(k, v) for k, v in children if "__is_file__" in v]

                all_children = sorted(dirs) + sorted(files)

                for i, (child_name, child_node) in enumerate(all_children):
                    is_last_child = i == len(all_children) - 1
                    render_node(child_node, child_name, new_prefix, is_last_child)

        render_node(tree, "", "", True)
        return "\n".join(lines)
