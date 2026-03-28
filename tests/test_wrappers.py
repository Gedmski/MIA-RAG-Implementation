from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_mia_rag_attack_wrapper_help():
    result = subprocess.run(
        [sys.executable, "mia_rag_attack.py", "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--config" in result.stdout


def test_process_results_wrapper_help():
    result = subprocess.run(
        [sys.executable, "process_results.py", "--help"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--input" in result.stdout
