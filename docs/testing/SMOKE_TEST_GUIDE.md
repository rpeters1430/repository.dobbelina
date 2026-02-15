# Cumination Smoke Testing System

A comprehensive automated testing system that analyzes site implementations and generates appropriate tests based on each site's actual structure.

## Quick Start

```bash
# 1. Analyze all sites (understand their structure)
python scripts/analyze_sites.py

# 2. Generate smoke tests based on analysis
python scripts/generate_smoke_tests.py

# 3. Run the smoke tests
python scripts/run_smoke_tests.py

# Or do all three steps at once:
python scripts/smoke_test_all.py
```

## What This System Does

### 1. Site Analysis (`analyze_sites.py`)

Analyzes each site module to understand:
- **What functions are registered** (Main, List, Playvid, Categories, Search, etc.)
- **What the entry point is** (default_mode=True)
- **Whether it uses BeautifulSoup or regex** for parsing
- **What parameters each function expects** (url, keyword, name, etc.)
- **Whether it's a webcam/live site** (different testing requirements)

**Output**: `results/site_analysis.json` - Complete site structure inventory

**Usage**:
```bash
# Analyze all sites
python scripts/analyze_sites.py

# View the analysis
cat results/site_analysis.json | jq '.summary'
```

**Example Output**:
```
Cumination Site Analyzer
============================================================

Found 145 sites

Analyzing sites...
  [  1/145] 6xtube                         ✅ [BS] [  ] 4 functions
  [  2/145] absoluporn                     ✅ [BS] [  ] 3 functions
  [  3/145] chaturbate                     ✅ [BS] [WC] 5 functions
  ...

Summary
============================================================
Total sites:           145
Successful imports:    143
Import errors:         2

BeautifulSoup sites:   126
Regex-only sites:      17
SoupSiteSpec sites:    15
Webcam sites:          8

Sites with Main:       143
Sites with List:       140
Sites with Categories: 98
Sites with Search:     112
Sites with Play:       142
```

### 2. Test Generation (`generate_smoke_tests.py`)

Generates pytest-based smoke tests tailored to each site's capabilities:

- **Main Test**: Verifies the entry point returns items
- **List Test**: Verifies video listing returns videos with metadata
- **Search Test**: Verifies search functionality works
- **Play Test**: Placeholder for playback URL extraction (needs fixtures)

**Output**: `tests/smoke_generated/test_smoke_*.py` - Individual test files per site

**Usage**:
```bash
# Generate tests for all sites
python scripts/generate_smoke_tests.py

# Generate tests for specific sites
python scripts/generate_smoke_tests.py --site pornhub xvideos

# Preview without writing files
python scripts/generate_smoke_tests.py --dry-run --site pornhub

# Custom output directory
python scripts/generate_smoke_tests.py --output-dir tests/my_smoke_tests
```

**Generated Test Example**:
```python
"""Smoke tests for pornhub site"""

import pytest
from resources.lib.sites import pornhub
from resources.lib import utils


class TestMain:
    """Test Main/default entry point"""

    def test_main_returns_items(self, site_object, captured_items, mock_gethtml):
        """Main should return at least one item"""
        # ... test implementation
```

### 3. Test Running (`run_smoke_tests.py`)

Runs the generated tests using pytest with proper Kodi mocks and generates reports:

**Output**:
- `results/smoke_test_report.json` - Detailed JSON report
- `results/smoke_test_report.md` - Human-readable Markdown report

**Usage**:
```bash
# Run all smoke tests
python scripts/run_smoke_tests.py

# Run tests for specific sites
python scripts/run_smoke_tests.py --site pornhub xvideos

# Generate and run in one command
python scripts/run_smoke_tests.py --generate

# Verbose output (see pytest details)
python scripts/run_smoke_tests.py --verbose

# Custom test directory
python scripts/run_smoke_tests.py --test-dir tests/my_smoke_tests
```

**Example Output**:
```
Testing 145 sites...

[  1/145] pornhub                       ✅ PASS      (3/3)
[  2/145] xvideos                       ✅ PASS      (3/3)
[  3/145] chaturbate                    ⚠️ SKIP      (0/0)
[  4/145] broken_site                   ❌ FAIL      (1/3)
...

============================================================
Smoke Test Summary
============================================================
Total sites tested:  145
  PASSED:            120 (82.8%)
  FAILED:            15
  SKIPPED:           8
  ERRORS:            2

Sites needing BeautifulSoup migration (10):
  - site1
  - site2
  ...

Sites needing fixes (5):
  - brokensite1
  - brokensite2
  ...
```

## Integration with Existing Tests

The smoke tests use the **same Kodi mocks** as your existing pytest tests (`tests/conftest.py`), so they accurately simulate the Kodi environment.

### Differences from `live_smoke_test.py`

| Feature | `live_smoke_test.py` | New System |
|---------|----------------------|------------|
| **Kodi Mocks** | Custom stubs | Uses conftest.py fixtures |
| **Test Framework** | Custom subprocess runner | Native pytest |
| **Site Analysis** | Runtime only | Pre-analyzed structure |
| **Test Generation** | Hardcoded flow | Generated per site |
| **Reports** | JSON + MD | JSON + MD + pytest |
| **Integration** | Standalone | Integrates with pytest suite |

## Workflow Examples

### Scenario 1: Test a Specific Site

```bash
# 1. Analyze the site
python scripts/analyze_sites.py

# 2. Check what functions it has
cat results/site_analysis.json | jq '.sites[] | select(.name == "pornhub")'

# 3. Generate tests for it
python scripts/generate_smoke_tests.py --site pornhub

# 4. Run the tests
python scripts/run_smoke_tests.py --site pornhub --verbose
```

### Scenario 2: Find Sites That Need Fixes

```bash
# 1. Run all smoke tests
python scripts/run_smoke_tests.py --generate

# 2. Check the report
cat results/smoke_test_report.json | jq '.categories'

# 3. Look at failures
cat results/smoke_test_report.json | jq '.results[] | select(.status == "FAIL")'
```

### Scenario 3: Test After BeautifulSoup Migration

```bash
# After migrating a site to BeautifulSoup:

# 1. Verify it's now detected as using BS
python scripts/analyze_sites.py
cat results/site_analysis.json | jq '.sites[] | select(.name == "mysite") | .uses_beautifulsoup'

# 2. Generate fresh tests
python scripts/generate_smoke_tests.py --site mysite

# 3. Run tests to verify migration
python scripts/run_smoke_tests.py --site mysite --verbose
```

### Scenario 4: Continuous Integration

```bash
# Add to CI pipeline:

# Run smoke tests and fail if any sites broken
python scripts/analyze_sites.py
python scripts/generate_smoke_tests.py
python scripts/run_smoke_tests.py

# Exit code is non-zero if tests fail
```

## Understanding the Reports

### site_analysis.json Structure

```json
{
  "summary": {
    "total_sites": 145,
    "beautifulsoup_sites": 126,
    "regex_only_sites": 19,
    "webcam_sites": 8,
    "with_main": 143,
    "with_list": 140,
    ...
  },
  "sites": [
    {
      "name": "pornhub",
      "display_name": "Pornhub",
      "base_url": "https://www.pornhub.com",
      "uses_beautifulsoup": true,
      "registered_functions": [
        {
          "name": "Main",
          "full_mode": "pornhub.Main",
          "is_default": true,
          "parameters": ["url"],
          ...
        }
      ],
      ...
    }
  ],
  "migration_status": {
    "beautifulsoup": ["pornhub", "xvideos", ...],
    "regex_only": ["oldsite1", "oldsite2", ...],
    ...
  }
}
```

### smoke_test_report.json Structure

```json
{
  "timestamp": "2025-02-14T10:30:00",
  "summary": {
    "total": 145,
    "passed": 120,
    "failed": 15,
    "pass_rate": 82.8
  },
  "results": [
    {
      "site": "pornhub",
      "status": "PASS",
      "tests_run": 3,
      "tests_passed": 3,
      "tests_failed": 0
    }
  ],
  "categories": {
    "needs_migration": ["oldsite1", ...],
    "needs_fixes": ["brokensite1", ...],
    "webcam_sites": ["chaturbate", ...]
  }
}
```

## Advanced Usage

### Custom Test Logic

You can edit generated tests in `tests/smoke_generated/` to add site-specific logic:

```python
# tests/smoke_generated/test_smoke_pornhub.py

class TestPlayback:
    """Test video playback URL extraction"""

    def test_playvid_extracts_m3u8(self, site_object, monkeypatch):
        """Pornhub should extract HLS stream URL"""
        # Add custom test logic here with real fixtures
        from tests.conftest import read_fixture

        html = read_fixture('pornhub_play.html')
        # ... test implementation
```

### Filtering Sites

```bash
# Test only BeautifulSoup-migrated sites
cat results/site_analysis.json | jq -r '.migration_status.beautifulsoup[]' | \
    xargs python scripts/run_smoke_tests.py --site

# Test only regex sites (need migration)
cat results/site_analysis.json | jq -r '.migration_status.regex_only[]' | \
    xargs python scripts/run_smoke_tests.py --site
```

## Troubleshooting

### "Site analysis not found"

**Solution**: Run `python scripts/analyze_sites.py` first

### "No test file generated"

**Solution**: Run `python scripts/generate_smoke_tests.py` or use `--generate` flag

### Tests fail with import errors

**Solution**: Make sure you're in the virtual environment and have run `pip install -r requirements-test.txt`

### All tests are SKIP

This is normal for:
- **Webcam sites**: Can't test without real browser/websocket
- **Sites missing functions**: May only have Main without List/Search

## Next Steps

1. **Add HTML Fixtures**: Create `tests/fixtures/sitename/` with real HTML samples
2. **Enhance Play Tests**: Use fixtures to test actual video URL extraction
3. **Integration Tests**: Combine with existing site-specific tests
4. **CI Integration**: Add smoke tests to GitHub Actions workflow

## See Also

- `CLAUDE.md` - Main development guide
- `MODERNIZATION.md` - BeautifulSoup migration tracking
- `tests/README.md` - Testing infrastructure documentation
- `scripts/live_smoke_test.py` - Original live smoke test (comparison)
