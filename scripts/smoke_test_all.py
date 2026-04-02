#!/usr/bin/env python3
"""All-in-one Smoke Test Runner

Runs the complete smoke testing workflow:
1. Analyze all sites
2. Generate smoke tests
3. Run smoke tests
4. Display results
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _python_has_module(python_executable: str, module_name: str) -> bool:
    result = subprocess.run(
        [python_executable, '-c', f'import {module_name}'],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def resolve_workflow_python() -> str:
    """Prefer the current interpreter, but fall back to the repo venv for pytest-driven steps."""
    candidates = [
        sys.executable,
        str(ROOT / '.venv' / 'bin' / 'python'),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists() and _python_has_module(candidate, 'pytest'):
            return candidate
    return sys.executable


def run_command(description: str, cmd: list[str], **kwargs) -> int:
    """Run a command and display progress"""
    print()
    print("=" * 60)
    print(description)
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(ROOT), **kwargs)

    if result.returncode != 0:
        print(f"\n❌ {description} FAILED (exit code {result.returncode})")
        return result.returncode

    print(f"\n✅ {description} COMPLETED")
    return 0


def load_smoke_summary() -> dict | None:
    report_path = ROOT / 'results' / 'smoke_test_report.json'
    if not report_path.exists():
        return None
    try:
        return json.loads(report_path.read_text(encoding='utf-8')).get('summary', {})
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Run complete smoke testing workflow'
    )
    parser.add_argument(
        '--site', nargs='+',
        help='Test specific sites only'
    )
    parser.add_argument(
        '--skip-analysis', action='store_true',
        help='Skip site analysis (use existing analysis)'
    )
    parser.add_argument(
        '--skip-generation', action='store_true',
        help='Skip test generation (use existing tests)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    args = parser.parse_args()

    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Cumination Smoke Test Suite" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")

    workflow_python = resolve_workflow_python()
    if workflow_python != sys.executable:
        print(f"Using test runner interpreter: {workflow_python}")

    # Step 1: Analyze sites
    if not args.skip_analysis:
        rc = run_command(
            "Step 1: Analyzing Site Structures",
            [workflow_python, 'scripts/analyze_sites.py']
        )
        if rc != 0:
            return rc
    else:
        print("\n⏭️  Skipping site analysis (using existing)")

    # Step 2: Generate tests
    if not args.skip_generation:
        cmd = [workflow_python, 'scripts/generate_smoke_tests.py']
        if args.site:
            cmd.extend(['--site'] + args.site)

        rc = run_command(
            "Step 2: Generating Smoke Tests",
            cmd
        )
        if rc != 0:
            return rc
    else:
        print("\n⏭️  Skipping test generation (using existing)")

    # Step 3: Run tests
    cmd = [workflow_python, 'scripts/run_smoke_tests.py']
    if args.site:
        cmd.extend(['--site'] + args.site)
    if args.verbose:
        cmd.append('--verbose')

    rc = run_command(
        "Step 3: Running Smoke Tests",
        cmd
    )

    # Final summary
    print()
    print("=" * 60)
    print("Workflow Complete")
    print("=" * 60)

    summary = load_smoke_summary()
    if rc == 0 and summary:
        if summary.get('passed', 0) > 0 and summary.get('failed', 0) == 0 and summary.get('errors', 0) == 0:
            print("✅ Smoke tests passed for the sites that executed.")
        elif summary.get('skipped', 0) == summary.get('total', 0):
            print("⚠️  All smoke tests were skipped - check the report for reasons.")
        else:
            print("✅ Smoke test workflow completed.")
    elif rc == 0:
        print("✅ Smoke test workflow completed.")
    else:
        print("⚠️  Tests or test setup failed - check reports for details")

    print()
    print("Reports available at:")
    print(f"  - results/site_analysis.json")
    print(f"  - results/smoke_test_report.json")
    print(f"  - results/smoke_test_report.md")
    print()

    return rc


if __name__ == '__main__':
    sys.exit(main())
