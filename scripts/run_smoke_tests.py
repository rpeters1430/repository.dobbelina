#!/usr/bin/env python3
"""Smart Smoke Test Runner for Cumination Sites

Runs smoke tests using pytest with proper Kodi mocks.
Generates actionable reports showing what works and what's broken.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parents[1]


def load_site_analysis() -> Dict[str, Any]:
    """Load site analysis report"""
    analysis_path = ROOT / 'results' / 'site_analysis.json'
    if not analysis_path.exists():
        print("ERROR: Site analysis not found. Run: python scripts/analyze_sites.py")
        sys.exit(1)

    return json.loads(analysis_path.read_text(encoding='utf-8'))


def run_pytest_for_site(site_name: str, test_dir: Path, verbose: bool = False) -> Dict[str, Any]:
    """Run pytest for a specific site and capture results"""
    test_file = test_dir / f"test_smoke_{site_name}.py"

    if not test_file.exists():
        return {
            'site': site_name,
            'status': 'SKIP',
            'reason': 'No test file generated',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
        }

    # Run pytest with JSON report
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_file),
        '--tb=short',
        '-v' if verbose else '-q',
        '--json-report',
        '--json-report-file=' + str(ROOT / 'results' / f'pytest_{site_name}.json'),
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Parse pytest output
        passed = result.stdout.count(' PASSED')
        failed = result.stdout.count(' FAILED')
        skipped = result.stdout.count(' SKIPPED')
        total = passed + failed + skipped

        if result.returncode == 0:
            status = 'PASS'
        elif failed > 0:
            status = 'FAIL'
        else:
            status = 'SKIP'

        return {
            'site': site_name,
            'status': status,
            'tests_run': total,
            'tests_passed': passed,
            'tests_failed': failed,
            'tests_skipped': skipped,
            'output': result.stdout,
            'errors': result.stderr,
        }

    except subprocess.TimeoutExpired:
        return {
            'site': site_name,
            'status': 'TIMEOUT',
            'reason': 'Test execution timed out',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
        }
    except Exception as e:
        return {
            'site': site_name,
            'status': 'ERROR',
            'reason': str(e),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
        }


def generate_report(results: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive test report"""
    total = len(results)
    passed = [r for r in results if r['status'] == 'PASS']
    failed = [r for r in results if r['status'] == 'FAIL']
    skipped = [r for r in results if r['status'] == 'SKIP']
    errors = [r for r in results if r['status'] in ('ERROR', 'TIMEOUT')]

    # Categorize failures
    needs_migration = []
    needs_fixes = []
    webcam_sites = []

    for r in failed:
        site_info = next((s for s in analysis['sites'] if s['name'] == r['site']), None)
        if site_info:
            if site_info['is_webcam']:
                webcam_sites.append(r['site'])
            elif not site_info['uses_beautifulsoup']:
                needs_migration.append(r['site'])
            else:
                needs_fixes.append(r['site'])

    return {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total,
            'passed': len(passed),
            'failed': len(failed),
            'skipped': len(skipped),
            'errors': len(errors),
            'pass_rate': round(len(passed) / total * 100, 1) if total > 0 else 0,
        },
        'results': results,
        'categories': {
            'needs_migration': needs_migration,
            'needs_fixes': needs_fixes,
            'webcam_sites': webcam_sites,
        },
    }


def print_summary(report: Dict[str, Any]):
    """Print test summary to console"""
    summary = report['summary']

    print()
    print("=" * 60)
    print("Smoke Test Summary")
    print("=" * 60)
    print(f"Total sites tested:  {summary['total']}")
    print(f"  PASSED:            {summary['passed']} ({summary['pass_rate']}%)")
    print(f"  FAILED:            {summary['failed']}")
    print(f"  SKIPPED:           {summary['skipped']}")
    print(f"  ERRORS:            {summary['errors']}")
    print()

    # Failures by category
    cats = report['categories']
    if cats['needs_migration']:
        print(f"Sites needing BeautifulSoup migration ({len(cats['needs_migration'])}):")
        for site in cats['needs_migration']:
            print(f"  - {site}")
        print()

    if cats['needs_fixes']:
        print(f"Sites needing fixes ({len(cats['needs_fixes'])}):")
        for site in cats['needs_fixes']:
            print(f"  - {site}")
        print()

    if cats['webcam_sites']:
        print(f"Webcam sites (expected limitations) ({len(cats['webcam_sites'])}):")
        for site in cats['webcam_sites']:
            print(f"  - {site}")
        print()


def save_report(report: Dict[str, Any], output_path: Path):
    """Save report to JSON and Markdown"""
    # Save JSON
    json_path = output_path.with_suffix('.json')
    json_path.write_text(json.dumps(report, indent=2), encoding='utf-8')

    # Generate Markdown
    md_lines = [
        "# Cumination Smoke Test Report",
        "",
        f"Generated: `{report['timestamp']}`",
        "",
        "## Summary",
        "",
        f"- Total sites: {report['summary']['total']}",
        f"- Passed: {report['summary']['passed']} ({report['summary']['pass_rate']}%)",
        f"- Failed: {report['summary']['failed']}",
        f"- Skipped: {report['summary']['skipped']}",
        f"- Errors: {report['summary']['errors']}",
        "",
        "## Results by Site",
        "",
        "| Site | Status | Tests | Passed | Failed | Skipped |",
        "|------|--------|-------|--------|--------|---------|",
    ]

    for r in report['results']:
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⚠️',
            'ERROR': '💥',
            'TIMEOUT': '⏱️',
        }.get(r['status'], '?')

        md_lines.append(
            f"| {r['site']} | {status_icon} {r['status']} | "
            f"{r.get('tests_run', 0)} | {r.get('tests_passed', 0)} | "
            f"{r.get('tests_failed', 0)} | {r.get('tests_skipped', 0)} |"
        )

    # Add failure categories
    cats = report['categories']
    if cats['needs_migration'] or cats['needs_fixes']:
        md_lines.extend([
            "",
            "## Action Items",
            "",
        ])

    if cats['needs_migration']:
        md_lines.extend([
            f"### Sites Needing BeautifulSoup Migration ({len(cats['needs_migration'])})",
            "",
            "These sites still use regex parsing and should be migrated:",
            "",
        ])
        for site in cats['needs_migration']:
            md_lines.append(f"- `{site}`")
        md_lines.append("")

    if cats['needs_fixes']:
        md_lines.extend([
            f"### Sites Needing Fixes ({len(cats['needs_fixes'])})",
            "",
            "These sites use BeautifulSoup but have failing tests:",
            "",
        ])
        for site in cats['needs_fixes']:
            md_lines.append(f"- `{site}`")
        md_lines.append("")

    md_path = output_path.with_suffix('.md')
    md_path.write_text('\n'.join(md_lines), encoding='utf-8')

    print(f"Reports saved:")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")


def main():
    parser = argparse.ArgumentParser(description='Run smoke tests for Cumination sites')
    parser.add_argument('--site', nargs='+', help='Specific sites to test')
    parser.add_argument('--test-dir', default='tests/smoke_generated',
                        help='Directory containing generated tests')
    parser.add_argument('--output', default='results/smoke_test_report',
                        help='Output path for report (without extension)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose pytest output')
    parser.add_argument('--generate', action='store_true',
                        help='Generate tests before running')
    args = parser.parse_args()

    # Generate tests first if requested
    if args.generate:
        print("Generating tests...")
        cmd = [sys.executable, 'scripts/generate_smoke_tests.py']
        if args.site:
            cmd.extend(['--site'] + args.site)
        subprocess.run(cmd, cwd=str(ROOT))
        print()

    # Load analysis
    print("Loading site analysis...")
    analysis = load_site_analysis()

    # Determine which sites to test
    test_dir = ROOT / args.test_dir
    if not test_dir.exists():
        print(f"ERROR: Test directory not found: {test_dir}")
        print("Run with --generate to create tests first")
        sys.exit(1)

    if args.site:
        sites_to_test = args.site
    else:
        # Find all test files
        sites_to_test = [
            f.stem.replace('test_smoke_', '')
            for f in test_dir.glob('test_smoke_*.py')
        ]

    print(f"Testing {len(sites_to_test)} sites...")
    print()

    # Run tests for each site
    results = []
    for i, site_name in enumerate(sites_to_test, 1):
        print(f"[{i:>3}/{len(sites_to_test)}] {site_name:<30}", end='', flush=True)
        result = run_pytest_for_site(site_name, test_dir, args.verbose)
        results.append(result)

        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⚠️',
            'ERROR': '💥',
            'TIMEOUT': '⏱️',
        }.get(result['status'], '?')

        print(f" {status_icon} {result['status']:<8} "
              f"({result.get('tests_passed', 0)}/{result.get('tests_run', 0)})")

    # Generate report
    print()
    print("Generating report...")
    report = generate_report(results, analysis)

    # Print summary
    print_summary(report)

    # Save reports
    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_report(report, output_path)

    # Exit code based on failures
    return 0 if report['summary']['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
