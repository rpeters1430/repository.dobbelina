#!/usr/bin/env python3
"""Update the project's .venv with the latest allowed versions of requirements-test.txt.

Usage:
    python scripts/update_venv.py          # upgrade pip + all deps in .venv
    python scripts/update_venv.py --create # create .venv first if missing
"""
import argparse
import subprocess
import sys
import venv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = REPO_ROOT / ".venv"
REQUIREMENTS = REPO_ROOT / "requirements-test.txt"


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd: list[str]) -> None:
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--create", action="store_true", help="create .venv if it doesn't exist"
    )
    args = parser.parse_args()

    if not VENV_DIR.exists():
        if not args.create:
            print(f"{VENV_DIR} does not exist. Re-run with --create to create it.")
            return 1
        print(f"Creating virtual environment at {VENV_DIR}")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    python = venv_python()
    if not python.exists():
        print(f"Could not find venv python at {python}")
        return 1

    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-r",
            str(REQUIREMENTS),
        ]
    )
    print("\nVirtual environment dependencies updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
