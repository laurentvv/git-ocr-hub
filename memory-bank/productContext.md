# Product Context: Git OCR Hub

## Why this Project Exists
Managing dozens of Git repositories manually leads to stale repositories, missed upstream updates, uncommitted code drift, and inconsistent code review quality. Cloud-based code review solutions often send sensitive source code off-site, require API subscriptions, or have latency/privacy concerns.

`git-ocr-hub` solves this by orchestrating repository discovery, automated fast-forward synchronization, and triggering deep AI code reviews using local hardware.

## User Experience & Workflows
1. **At-a-glance Supervision**: Run `run-hub.ps1 status` to see all 53 repositories across `C:\GIT` and `D:\GIT` categorized by branch, clean/dirty state, and upstream delta.
2. **Safe Automated Sync**: Run `run-hub.ps1 sync` to pull clean repositories without risk to uncommitted modifications.
3. **Targeted Diff Reviews**: Inspect pending changes before committing or pushing (`run-hub.ps1 review`).
4. **Full Deep Code Audits**: Audit entire repositories with `run-hub.ps1 scan -Repo "..."` to catch bugs, memory safety issues, and design anti-patterns.
5. **Interactive Exploration**: Open `reports/index.html` in any browser to filter repositories and view detailed findings in individual HTML reports.
