#!/usr/bin/env python3
"""All-in-one Smoke Test Runner

Runs the complete smoke testing workflow:
1. Analyze all sites
2. Generate smoke tests
3. Run smoke tests
4. Display results
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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

    # Step 1: Analyze sites
    if not args.skip_analysis:
        rc = run_command(
            "Step 1: Analyzing Site Structures",
            [sys.executable, 'scripts/analyze_sites.py']
        )
        if rc != 0:
            return rc
    else:
        print("\n⏭️  Skipping site analysis (using existing)")

    # Step 2: Generate tests
    if not args.skip_generation:
        cmd = [sys.executable, 'scripts/generate_smoke_tests.py']
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
    cmd = [sys.executable, 'scripts/run_smoke_tests.py']
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

    if rc == 0:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed - check reports for details")

    print()
    print("Reports available at:")
    print(f"  - results/site_analysis.json")
    print(f"  - results/smoke_test_report.json")
    print(f"  - results/smoke_test_report.md")
    print()

    return rc


if __name__ == '__main__':
    sys.exit(main())
