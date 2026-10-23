import os
import subprocess
from typing import Dict, List, Optional, Any

class GitManager:
    """Manages Git repository discovery, status checking, and safe synchronization."""

    def __init__(self, roots: List[str], excluded_repos: Optional[List[str]] = None):
        self.roots = roots
        self.excluded_repos = set(excluded_repos or [])

    def find_repositories(self) -> List[str]:
        """Discover all Git repositories located inside monitored roots."""
        repos = []
        for root in self.roots:
            if not os.path.exists(root):
                continue
            try:
                for entry in os.scandir(root):
                    if not entry.is_dir():
                        continue
                    if entry.name in self.excluded_repos:
                        continue
                    git_dir = os.path.join(entry.path, ".git")
                    if os.path.exists(git_dir):
                        repos.append(os.path.abspath(entry.path))
            except PermissionError:
                continue
        return sorted(repos)

    def run_git(self, repo_path: str, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Execute a git command within a repository."""
        cmd = ["git", "-C", repo_path] + args
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    def get_repo_status(self, repo_path: str) -> Dict[str, Any]:
        """Analyze full status of a repository."""
        name = os.path.basename(repo_path)
        
        # Branch
        cp_branch = self.run_git(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
        branch = cp_branch.stdout.strip() if cp_branch.returncode == 0 else "UNKNOWN"

        # Remotes
        cp_remotes = self.run_git(repo_path, ["remote"])
        remotes = [r.strip() for r in cp_remotes.stdout.splitlines() if r.strip()]

        # Dirty files
        cp_status = self.run_git(repo_path, ["status", "--porcelain"])
        dirty_lines = [line for line in cp_status.stdout.splitlines() if line.strip()]
        is_dirty = len(dirty_lines) > 0

        # Upstream check
        upstream = None
        behind = 0
        ahead = 0
        if remotes:
            cp_up = self.run_git(repo_path, ["rev-parse", "--abbrev-ref", "@{u}"])
            if cp_up.returncode == 0:
                upstream = cp_up.stdout.strip()
                cp_rev = self.run_git(repo_path, ["rev-list", "--left-right", "--count", f"{upstream}...HEAD"])
                if cp_rev.returncode == 0:
                    parts = cp_rev.stdout.strip().split()
                    if len(parts) == 2:
                        behind = int(parts[0])
                        ahead = int(parts[1])

        # Last commit info
        cp_log = self.run_git(repo_path, ["log", "-1", "--format=%H|%an|%ad|%s", "--date=short"])
        last_commit = {}
        if cp_log.returncode == 0 and cp_log.stdout.strip():
            c_parts = cp_log.stdout.strip().split("|", 3)
            if len(c_parts) == 4:
                last_commit = {
                    "hash": c_parts[0],
                    "author": c_parts[1],
                    "date": c_parts[2],
                    "subject": c_parts[3],
                }

        return {
            "name": name,
            "path": repo_path,
            "branch": branch,
            "remotes": remotes,
            "has_remote": len(remotes) > 0,
            "upstream": upstream,
            "is_dirty": is_dirty,
            "dirty_count": len(dirty_lines),
            "dirty_files": dirty_lines[:15],
            "behind": behind,
            "ahead": ahead,
            "last_commit": last_commit,
        }

    def fetch_all(self, repo_path: str) -> bool:
        """Fetch remote updates silently."""
        cp = self.run_git(repo_path, ["fetch", "--all", "--prune", "--quiet"], timeout=60)
        return cp.returncode == 0

    def pull_fast_forward(self, repo_path: str) -> Dict[str, Any]:
        """Safely pull latest changes if fast-forward is possible."""
        cp = self.run_git(repo_path, ["pull", "--ff-only"])
        return {
            "success": cp.returncode == 0,
            "output": cp.stdout.strip() if cp.returncode == 0 else cp.stderr.strip()
        }
