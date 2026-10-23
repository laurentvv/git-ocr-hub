# Technical Context: Git OCR Hub

## Hardware & Acceleration
- **GPU**: AMD Radeon RX 6950 XT (16,384 MB VRAM, gfx1030).
- **RAM**: 32 GB system memory.
- **Drives**: NVMe C: (OS & fast workspace), External D: (mass storage for large GGUFs and archive repositories).

## Local LLM Configuration (`llama-server`)
- **Primary Model**: `D:\Modeles_LLM\Qwen3.8-27B-Uncensored-IQ3_M.gguf` (13.9 GB).
- **Secondary Model**: `C:\Modeles_LLM\Ornith-1.5-9B-Q6_K.gguf` (7.0 GB).
- **Optimal Launch Flags**:
  ```powershell
  llama-server.exe -m "D:\Modeles_LLM\Qwen3.8-27B-Uncensored-IQ3_M.gguf" `
    -c 32768 `
    -ctk q4_0 -ctv q4_0 `
    -ngl 99 `
    --flash-attn on `
    --reasoning-budget 512 `
    --no-reasoning-preserve `
    -np 1 `
    --port 8080 `
    --alias "Qwen-27B" `
    --jinja
  ```
- **VRAM Footprint**: ~14.9 GB / 16.0 GB (100% in VRAM, zero system RAM spillover).
- **Performance**:
  - Prompt Processing: ~120 to 180 tokens/sec.
  - Token Generation: ~13.9 to 14.2 tokens/sec.

## Tooling & Software Stack
- **CLI**: `@alibaba-group/open-code-review` v1.13.3.
- **Node.js**: v22.x on Windows 11.
- **Python**: 3.13 (configured with UTF-8 encoding safeguard).
- **Shell**: PowerShell 7.x.
