import json
import os
import shutil
import subprocess
import urllib.request
from typing import Dict, Any, Optional

class OcrRunner:
    """Manages OpenCodeReview (ocr) CLI interactions and LLM connectivity."""

    def __init__(self, server_url: str = "http://127.0.0.1:8080/v1", provider: str = "local_llama", model: str = "Ornith 1.5 9B (C:)"):
        self.server_url = server_url
        self.provider = provider
        self.model = model
        self.ocr_cmd = shutil.which("ocr") or "ocr"

    def is_server_alive(self, timeout: float = 2.0) -> bool:
        """Check if local llama-server OpenAI endpoint is responsive."""
        try:
            # Check models endpoint
            url = f"{self.server_url.rstrip('/')}/models"
            req = urllib.request.Request(url, headers={"User-Agent": "git-ocr-hub"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.status in (200, 204)
        except Exception:
            return False

    def check_ocr_installed(self) -> bool:
        """Check if ocr command is available in system PATH."""
        try:
            cp = subprocess.run([self.ocr_cmd, "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return cp.returncode == 0
        except Exception:
            return False

    def test_llm_connection(self) -> Dict[str, Any]:
        """Run `ocr llm test` to verify connection and tool calling."""
        try:
            cp = subprocess.run([self.ocr_cmd, "llm", "test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            return {
                "success": cp.returncode == 0,
                "output": cp.stdout.strip() if cp.returncode == 0 else cp.stderr.strip()
            }
        except Exception as e:
            return {"success": False, "output": str(e)}

    def preview_review(self, repo_path: str, commit: Optional[str] = None) -> Dict[str, Any]:
        """Preview which files will be reviewed without sending requests to LLM."""
        args = [self.ocr_cmd, "review", "--repo", repo_path, "--preview"]
        if commit:
            args.extend(["-c", commit])
        
        cp = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        return {
            "success": cp.returncode == 0,
            "output": cp.stdout.strip()
        }

    def run_review(self, repo_path: str, commit: Optional[str] = None, timeout: int = 300) -> Dict[str, Any]:
        """Execute diff-based code review with structured JSON output."""
        args = [
            self.ocr_cmd, "review",
            "--repo", repo_path,
            "--format", "json",
            "--audience", "agent"
        ]
        if commit:
            args.extend(["-c", commit])

        try:
            cp = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout
            )
            raw_output = cp.stdout.strip()
            error_output = cp.stderr.strip()
            
            # Try parsing JSON output
            data = None
            if raw_output:
                try:
                    data = json.loads(raw_output)
                except json.JSONDecodeError:
                    # Sometimes logs are appended before JSON
                    lines = raw_output.splitlines()
                    for line in reversed(lines):
                        line = line.strip()
                        if line.startswith("{") and line.endswith("}"):
                            try:
                                data = json.loads(line)
                                break
                            except json.JSONDecodeError:
                                pass

            return {
                "success": cp.returncode == 0,
                "exit_code": cp.returncode,
                "parsed": data,
                "raw": raw_output,
                "stderr": error_output
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "parsed": None,
                "raw": "",
                "stderr": f"Review timed out after {timeout} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -2,
                "parsed": None,
                "raw": "",
                "stderr": str(e)
            }
