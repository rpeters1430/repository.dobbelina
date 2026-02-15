#!/usr/bin/env python3
"""Quick Smoke Check - Run pytest smoke tests and show actionable results"""

import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_smoke_tests(site_name=None, verbose=False):
    """Run smoke tests and parse results"""

    if site_name:
        # Test specific site
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_smoke_all_sites.py',
            '-k', site_name,
            '-v' if verbose else '-q',
            '--tb=short',
        ]
    else:
        # Test all sites
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/test_smoke_all_sites.py',
            '-v' if verbose else '-q',
            '--tb=line',
            '-x',  # Stop on first failure if checking specific site
        ] if site_name else [
            sys.executable, '-m', 'pytest',
            'tests/test_smoke_all_sites.py',
            '-q',
            '--tb=line',
        ]

    print("\nRunning smoke tests...")
    print("=" * 60)

    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

    # Parse output
    output = result.stdout + result.stderr

    # Count results from pytest summary line
    passed_match = re.search(r'(\d+) passed', output)
    failed_match = re.search(r'(\d+) failed', output)
    skipped_match = re.search(r'(\d+) skipped', output)
    error_match = re.search(r'(\d+) error', output)

    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    skipped = int(skipped_match.group(1)) if skipped_match else 0
    errors = int(error_match.group(1)) if error_match else 0

    print(output)
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped, {errors} errors")

    if failed > 0:
        print()
        print("Sites with failures:")
        # Extract failed test names
        for line in output.split('\n'):
            if 'FAILED' in line:
                # Extract site name from test name
                match = re.search(r'\[([^\]]+)\]', line)
                if match:
                    site = match.group(1)
                    print(f"  - {site}")

        print()
        print("To debug a specific site:")
        print("  python run_tests.py tests/test_smoke_all_sites.py::test_site_main_function_runs[sitename] -vv")

    return result.returncode


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Quick smoke check for Cumination sites')
    parser.add_argument('--site', help='Test specific site')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()

    return run_smoke_tests(args.site, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
