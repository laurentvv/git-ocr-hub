# OpenCodeReview & LLM Benchmarks Memory ⏱️📊

> **Persistent execution telemetry and empirical code review benchmarks.**  
> Records execution duration, lines of code (LOC), token throughput, and delays per line of code for local AI code reviews and whole-repository audits.

---

## 🖥️ Test Rig & Environment

- **Hardware**: AMD Ryzen 9 + AMD Radeon RX 6950 XT (16 GB VRAM)
- **OS**: Windows 11 Pro 64-bit
- **Local Backend**: `llama-server` (llama.cpp build 11829, Clang 20.1.8)
- **Model**: `Qwen3.8-27B-Uncensored-IQ3_M.gguf` (27.3B params, 13.89 GB, 3.66 bpw)
- **Engine Configuration**:
  - Context window: `32,768` tokens
  - KV Cache: `q4_0` (Key) / `q4_0` (Value) (~1.8 GB VRAM footprint)
  - Offload: `99` GPU layers (`-ngl 99`, all layers in VRAM, ~14.9 GB VRAM total)
  - Optimizations: Flash Attention `on`, Reasoning budget `512`
  - Chat Template: Jinja native tool calling enabled
- **Orchestration**: `git-ocr-hub` + OpenCodeReview CLI `v1.13.3`

---

## 📈 Consolidated Empirical Metrics

| Metric | Measured Value | Notes |
|---|---|---|
| **Prompt Evaluation Speed** | **100 – 135 tokens/s** | Boosted by LCP prefix prompt cache reuse |
| **Generation Speed** | **~11.5 tokens/s** | Qwen 27B on RX 6950 XT |
| **Average Delay per Line of Code** | **~0.20 s / line** (200 ms / LOC) | Including full AST tool calls & reasoning |
| **Average Line Throughput** | **~300 LOC / minute** | ~18,000 lines of code / hour |
| **Average Cycle per Target File** | **~75 seconds / file** | 2-3 tool call round trips per file |
| **Tool Calling Round Trip** | **~10 – 15 s** | `file_find`, `code_search`, `code_comment` |

---

## 📋 Run History & Benchmark Log

### Run #1 — `C:\GIT\blender-ia` (Full Repository Audit `scan`)
- **Date**: 2026-10-24 09:13:22 (In progress)
- **Repository Scope**: 4,584 changed/untracked items detected; 4,402 binaries/media excluded; **182 code & config files targeted**.
- **Composition**: 153 Python scripts (`.py`), 19 JSON schemas/manifests (`.json`), 2 HTML, 2 TOML, 6 configuration files.
- **Total Lines of Code (LOC)**: **34,416 lines**
- **Telemetry Checkpoint (at 39m 19s)**:
  - **Files Processed**: 30 files
  - **Lines of Code Processed**: **11,805 lines** (~34.3% completion)
  - **Total Elapsed**: 2,359 seconds (~39.3 minutes)
  - **Average Delay per LOC**: `2359s / 11805 LOC` = **0.1998 s/line (~200 ms/LOC)**
  - **Speed**: **~300 LOC / min**
  - **Remaining Lines**: 22,611 lines
  - **Estimated Remaining Duration**: `22611 * 0.20s` = ~4,520 seconds = **~75 minutes (1h15m)**
  - **Total Estimated Run Time**: ~114 minutes (~1h54m)

---

## 💡 Key Takeaways for Sizing Runs

1. **Diff Reviews (`review`)**:
   - Typical small PR or worktree diff (100 - 500 lines): **~20 to 100 seconds**.
   - Medium change set (1,000 - 2,000 lines): **~3 to 6 minutes**.
2. **Whole Repository Audits (`scan`)**:
   - Small repos (< 5,000 LOC): **~15 to 20 minutes**.
   - Medium repos (20,000 - 50,000 LOC): **~1 to 2.5 hours**.
   - Large repos (> 100,000 LOC): Recommend targeting critical subpaths (`--path src/core` or `--path extension/`) rather than scanning all files in a single pass.
