# System Patterns: Git OCR Hub

## High-Level Architecture

```
[Monitored Roots: C:\GIT, D:\GIT]
             │
             ▼
   [GitManager (core/git_manager.py)]
   - Discovery (os.scandir)
   - Status analysis (dirty, ahead, behind, branch, last commit)
   - Safe sync (git fetch, pull --ff-only)
             │
             ├──► [OcrRunner (core/ocr_runner.py)]
             │    - Health check on llama-server (:8080)
             │    - ocr review (diff-based)
             │    - ocr scan (full repository audit)
             │    - Tool call support (Jinja template)
             │
             ▼
   [Reporter (core/reporter.py)]
   - Markdown logs (reports/<repo>/<timestamp>.md)
   - Standalone HTML per-repo (reports/<repo>.html)
   - Master interactive HTML Dashboard (reports/index.html)
             │
             ▼
[User Interfaces: CLI orchestrator.py | PowerShell run-hub.ps1 | Browser WebUI]
```

## Key Architectural Principles
- **No Heavy Dependencies**: Standard library Python 3 + PowerShell + native binaries.
- **Fail-Safe Git Operations**: Never attempt rebase or recursive merges automatically; only `--ff-only`.
- **Decoupled LLM Layer**: Standard OpenAI-compatible API protocol (`/v1/chat/completions`) connecting OpenCodeReview to `llama-server`.
- **Standalone Static Reports**: All HTML reports are zero-dependency, self-contained, responsive, and render cleanly offline.
- **Empirical Benchmark Telemetry**: Track execution times, LOC counts, and token processing throughput across local models to predict duration and delay-per-line (see `docs/BENCHMARKS.md`).
