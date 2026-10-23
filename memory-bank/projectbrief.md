# Project Brief: Git OCR Hub

## Objective
`git-ocr-hub` is an automated Git supervision and local AI-powered code review/audit orchestrator. It manages 50+ Git repositories across multiple drives (`C:\GIT`, `D:\GIT`), safely synchronizes repositories, and runs deep code reviews and audits using local LLMs (via `llama.cpp` and OpenCodeReview CLI).

## Key Goals
1. **Safety First**: Never overwrite local uncommitted work (`--ff-only` on clean working trees, automatic protection of dirty repositories).
2. **Local AI Execution**: Fully offline, private code reviews powered by AMD Radeon RX 6950 XT (16 GB VRAM) running `llama-server`.
3. **Dual Review Capabilities**:
   - Diff-based review (`ocr review`) for uncommitted changes or specific commits.
   - Full repository code audit (`ocr scan`) without requiring any git diff.
4. **Rich Visualization**:
   - Master interactive HTML dashboard (`reports/index.html`) indexing all monitored repositories.
   - Dedicated standalone HTML reports (`reports/<repo_name>.html`) per repository with direct bi-directional navigation.
   - CLI + PowerShell interactive launcher (`run-hub.ps1`).
