# Cumination Development Scripts

This directory contains various development and testing utilities for the Cumination addon.

## Smoke Testing System (NEW!)

A comprehensive automated testing system that analyzes sites and generates appropriate tests.

### Quick Start

```bash
# Run everything at once
python scripts/smoke_test_all.py

# Or run individual steps:
python scripts/analyze_sites.py        # Analyze site structures
python scripts/generate_smoke_tests.py # Generate tests
python scripts/run_smoke_tests.py      # Run tests

# Check specific site status
python scripts/check_site_status.py pornhub

# List all sites with issues
python scripts/check_site_status.py
```

### Individual Tools

| Script | Purpose | Output |
|--------|---------|--------|
| `analyze_sites.py` | Analyze all site module structures | `results/site_analysis.json` |
| `generate_smoke_tests.py` | Generate pytest-based smoke tests | `tests/smoke_generated/*.py` |
| `run_smoke_tests.py` | Run generated tests and create reports | `results/smoke_test_report.{json,md}` |
| `smoke_test_all.py` | Run all three steps in sequence | All above outputs |
| `check_site_status.py` | Check status of specific site or list problems | Console output |

### Documentation

See **`SMOKE_TEST_GUIDE.md`** for comprehensive documentation including:
- Detailed usage instructions
- Workflow examples
- Report structure explanation
- Integration with existing tests
- Troubleshooting guide

## Other Scripts

### Logo Management

- `process_logos.py` - Batch process logo images
- `validate_logos.py` - Validate logo dimensions and format
- `find_missing_logos.py` - Identify sites without logos
- `auto_add_logos.py` - Automatically download and add missing logos
- `analyze_logos.py` - Analyze logo usage
- `analyze_logo_dimensions.py` - Check logo dimensions
- `get_logo_dimensions.py` - Get dimensions for specific logos
- `fix_all_logos.py` - Fix all logos in batch

**Requirements**: ImageMagick and pngquant (installed by `setup.sh` / `setup_windows.ps1`)

### Upstream Sync

- `check_upstream_sync.sh` - Check for new upstream commits
- `cherry_pick_with_tracking.sh` - Cherry-pick with automatic tracking

See `UPSTREAM_SYNC.md` for details.

### Legacy Testing

- `live_smoke_test.py` - Original live smoke test runner (superseded by new smoke testing system)

## Common Workflows

### Test a Site After Making Changes

```bash
# 1. Check current status
python scripts/check_site_status.py mysite

# 2. Make your changes to the site file
# edit plugin.video.cumination/resources/lib/sites/mysite.py

# 3. Re-analyze
python scripts/analyze_sites.py

# 4. Generate and run tests
python scripts/run_smoke_tests.py --generate --site mysite --verbose

# 5. Check new status
python scripts/check_site_status.py mysite
```

### Find Sites That Need Work

```bash
# List all problem sites
python scripts/check_site_status.py

# Check a specific category from analysis
cat results/site_analysis.json | jq -r '.migration_status.regex_only[]'

# Check test failures
cat results/smoke_test_report.json | jq -r '.categories'
```

### Test Before Committing

```bash
# Run smoke tests on all sites
python scripts/smoke_test_all.py

# Check for failures
if [ $? -ne 0 ]; then
    echo "Some tests failed - check results/smoke_test_report.md"
    cat results/smoke_test_report.md
fi
```

## Tips

1. **Always run `analyze_sites.py` first** - Other tools depend on this
2. **Check generated tests** - You can customize them in `tests/smoke_generated/`
3. **Add fixtures** - For better playback tests, add HTML fixtures in `tests/fixtures/sitename/`
4. **Use `--verbose`** - Get detailed pytest output when debugging
5. **Integrate with CI** - Add smoke tests to `.github/workflows/`

## See Also

- `../CLAUDE.md` - Main development guide
- `../MODERNIZATION.md` - BeautifulSoup migration tracking
- `../tests/README.md` - Testing infrastructure
- `SMOKE_TEST_GUIDE.md` - Comprehensive smoke testing guide
