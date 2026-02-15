#!/usr/bin/env python3
"""Site Status Checker

Analyzes a specific site and provides actionable information about what needs fixing.
Combines analysis data with test results to give a complete picture.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[1]


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file if it exists"""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None


def find_site_analysis(site_name: str) -> Optional[Dict[str, Any]]:
    """Find site in analysis results"""
    analysis = load_json_file(ROOT / 'results' / 'site_analysis.json')
    if not analysis:
        return None

    for site in analysis.get('sites', []):
        if site['name'] == site_name:
            return site

    return None


def find_site_test_results(site_name: str) -> Optional[Dict[str, Any]]:
    """Find site in test results"""
    report = load_json_file(ROOT / 'results' / 'smoke_test_report.json')
    if not report:
        return None

    for result in report.get('results', []):
        if result['site'] == site_name:
            return result

    return None


def print_site_status(site_name: str):
    """Print comprehensive site status"""
    print()
    print("=" * 60)
    print(f"Site Status: {site_name}")
    print("=" * 60)
    print()

    # Load analysis
    analysis = find_site_analysis(site_name)
    if not analysis:
        print("❌ Site not found in analysis")
        print()
        print("Run: python scripts/analyze_sites.py")
        return 1

    # Check for import error
    if analysis.get('import_error'):
        print("❌ IMPORT ERROR")
        print(f"   {analysis['import_error']}")
        print()
        print("This site cannot be loaded. Possible issues:")
        print("  - Syntax error in the .py file")
        print("  - Missing dependency")
        print("  - Invalid site object")
        print()
        print(f"Check: {analysis['source_file']}")
        return 1

    # Basic info
    print("📋 Basic Information")
    print(f"   Name:         {analysis['name']}")
    print(f"   Display Name: {analysis['display_name']}")
    print(f"   Base URL:     {analysis['base_url']}")
    print(f"   Source File:  {analysis['source_file']}")
    print(f"   Source Lines: {analysis['source_lines']}")
    print()

    # Capabilities
    print("⚙️  Capabilities")
    print(f"   Main Function:       {'✅' if analysis['has_main'] else '❌'}")
    print(f"   List Function:       {'✅' if analysis['has_list'] else '❌'}")
    print(f"   Categories:          {'✅' if analysis['has_categories'] else '❌'}")
    print(f"   Search:              {'✅' if analysis['has_search'] else '❌'}")
    print(f"   Play Function:       {'✅' if analysis['has_play'] else '❌'}")
    print(f"   Webcam/Live:         {'✅' if analysis['is_webcam'] else '❌'}")
    print()

    # Parsing method
    print("🔍 Parsing Method")
    print(f"   BeautifulSoup:       {'✅' if analysis['uses_beautifulsoup'] else '❌'}")
    print(f"   Regex:               {'✅' if analysis['uses_regex'] else '⚠️ '}")
    print(f"   SoupSiteSpec:        {'✅' if analysis['uses_soup_spec'] else '❌'}")
    print()

    if not analysis['uses_beautifulsoup']:
        print("⚠️  MIGRATION NEEDED")
        print("   This site uses regex parsing and should be migrated to BeautifulSoup")
        print("   See: MODERNIZATION.md and CLAUDE.md for migration guide")
        print()

    # Registered functions
    print(f"📝 Registered Functions ({len(analysis['registered_functions'])})")
    for func in analysis['registered_functions']:
        default = " [DEFAULT]" if func['is_default'] else ""
        clean = " [CLEAN]" if func['is_clean'] else ""
        params = ", ".join(func['parameters']) if func['parameters'] else "none"
        print(f"   - {func['name']}{default}{clean}")
        print(f"     Mode: {func['full_mode']}")
        print(f"     Params: {params}")
        print(f"     Location: {func['source_location']}")
        print()

    # Test results
    test_result = find_site_test_results(site_name)
    if test_result:
        print("🧪 Test Results")
        status = test_result['status']
        icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'SKIP': '⚠️',
            'ERROR': '💥',
            'TIMEOUT': '⏱️',
        }.get(status, '?')

        print(f"   Status:      {icon} {status}")
        print(f"   Tests Run:   {test_result.get('tests_run', 0)}")
        print(f"   Passed:      {test_result.get('tests_passed', 0)}")
        print(f"   Failed:      {test_result.get('tests_failed', 0)}")
        print(f"   Skipped:     {test_result.get('tests_skipped', 0)}")

        if test_result.get('reason'):
            print(f"   Reason:      {test_result['reason']}")

        print()

        if status == 'FAIL':
            print("❌ ACTION REQUIRED")
            print("   This site has failing tests.")
            print()
            print("   Next steps:")
            print(f"   1. Run tests: python run_tests.py tests/smoke_generated/test_smoke_{site_name}.py -v")
            print(f"   2. Check source: {analysis['source_file']}")
            print(f"   3. Add HTML fixtures if needed: tests/fixtures/{site_name}/")
            print()

            if test_result.get('output'):
                print("   Test output:")
                for line in test_result['output'].split('\n')[:20]:
                    if line.strip():
                        print(f"   {line}")
                print()

    else:
        print("🧪 Test Results")
        print("   No test results found.")
        print()
        print("   Run tests: python scripts/run_smoke_tests.py --site", site_name)
        print()

    # Recommendations
    print("💡 Recommendations")
    recommendations = []

    if not analysis['has_main']:
        recommendations.append("❌ Add a Main/default entry point function")

    if not analysis['has_play']:
        recommendations.append("❌ Add a Playvid function for video playback")

    if not analysis['uses_beautifulsoup'] and not analysis['is_webcam']:
        recommendations.append("⚠️  Migrate from regex to BeautifulSoup parsing")

    if analysis['uses_beautifulsoup'] and not analysis['uses_soup_spec']:
        recommendations.append("✨ Consider using SoupSiteSpec for cleaner code")

    if not analysis['has_search']:
        recommendations.append("💭 Consider adding Search functionality")

    if not analysis['has_categories']:
        recommendations.append("💭 Consider adding Categories functionality")

    test_status = test_result['status'] if test_result else 'UNKNOWN'
    if test_status == 'FAIL':
        recommendations.append("❌ Fix failing tests (see Test Results above)")
    elif test_status == 'SKIP':
        recommendations.append("⚠️  Tests are skipped - may need fixtures or live testing")
    elif test_status == 'PASS':
        recommendations.append("✅ All tests passing - site looks good!")

    if not recommendations:
        recommendations.append("✅ No issues found - site looks good!")

    for rec in recommendations:
        print(f"   {rec}")

    print()

    return 0 if test_status == 'PASS' else 1


def list_problem_sites():
    """List all sites with issues"""
    analysis = load_json_file(ROOT / 'results' / 'site_analysis.json')
    if not analysis:
        print("No analysis found. Run: python scripts/analyze_sites.py")
        return

    report = load_json_file(ROOT / 'results' / 'smoke_test_report.json')

    print()
    print("Sites with Issues")
    print("=" * 60)
    print()

    # Import errors
    errors = [s for s in analysis['sites'] if s.get('import_error')]
    if errors:
        print(f"Import Errors ({len(errors)}):")
        for site in errors:
            print(f"  - {site['name']}: {site['import_error'][:50]}")
        print()

    # Failed tests
    if report:
        failed = [r for r in report['results'] if r['status'] == 'FAIL']
        if failed:
            print(f"Failed Tests ({len(failed)}):")
            for result in failed:
                print(f"  - {result['site']}: {result.get('tests_failed', 0)} failures")
            print()

    # Missing critical functions
    no_main = [s['name'] for s in analysis['sites'] if not s.get('import_error') and not s['has_main']]
    no_play = [s['name'] for s in analysis['sites'] if not s.get('import_error') and not s['has_play']]

    if no_main:
        print(f"Missing Main Function ({len(no_main)}):")
        for site in no_main[:10]:
            print(f"  - {site}")
        if len(no_main) > 10:
            print(f"  ... and {len(no_main) - 10} more")
        print()

    if no_play:
        print(f"Missing Play Function ({len(no_play)}):")
        for site in no_play[:10]:
            print(f"  - {site}")
        if len(no_play) > 10:
            print(f"  ... and {len(no_play) - 10} more")
        print()

    # Needs migration
    needs_migration = [
        s['name'] for s in analysis['sites']
        if not s.get('import_error') and not s['uses_beautifulsoup'] and not s['is_webcam']
    ]
    if needs_migration:
        print(f"Needs BeautifulSoup Migration ({len(needs_migration)}):")
        for site in needs_migration[:10]:
            print(f"  - {site}")
        if len(needs_migration) > 10:
            print(f"  ... and {len(needs_migration) - 10} more")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Check status of specific sites or list problem sites'
    )
    parser.add_argument(
        'site', nargs='?',
        help='Site name to check (omit to list all problem sites)'
    )
    args = parser.parse_args()

    if args.site:
        return print_site_status(args.site)
    else:
        list_problem_sites()
        return 0


if __name__ == '__main__':
    sys.exit(main())
