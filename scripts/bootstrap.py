"""Create and populate a native virtual environment for the current OS."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"


def venv_python() -> Path:
    return VENV / (Path("Scripts") / "python.exe" if os.name == "nt" else Path("bin") / "python")


def run(command: list[str]) -> None:
    print("+", " ".join(str(part) for part in command))
    subprocess.check_call(command, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", default="requirements.lock.txt")
    args = parser.parse_args()

    interpreter = venv_python()
    if VENV.exists() and not interpreter.exists():
        print(f"Replacing incompatible virtual environment at {VENV}")
        shutil.rmtree(VENV)
    if not interpreter.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
    else:
        print(f"Using native virtual environment: {interpreter}")

    run([str(interpreter), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(interpreter), "-m", "pip", "install", "-r", str(ROOT / args.requirements)])
    print(f"Ready: {interpreter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
