# Live Smoke Testing (Read-Only)

Use `scripts/live_smoke_test.py` to test real site behavior without touching fixtures.

## What it checks

- `main`: site loads and returns menu/video entries
- `list`: videos load from a real listing URL
- `categories`: category page/folder entries load
- `search`: search returns videos for a keyword
- `play`: play mode resolves a playback URL from a sampled video item

Also reported per step:
- video item count
- screenshot/image count (`icon` present)
- description count (`desc` present)

## Important safety rule

This script is **read-only**:
- it does **not** write to `tests/fixtures/`
- it does **not** modify test data
- it only writes reports to `results/`

## Usage

Run all sites:

```bash
python scripts/live_smoke_test.py
```

Run a subset:

```bash
python scripts/live_smoke_test.py --site stripchat pornhub pornkai
```

Faster scan (no search/play):

```bash
python scripts/live_smoke_test.py --steps main,list,categories
```

Tune timeouts:

```bash
python scripts/live_smoke_test.py --timeout 35 --site-timeout 140
```

Custom output dir / search keyword:

```bash
python scripts/live_smoke_test.py --out reports --keyword sexy
```

## Output

Each run writes:

- `results/live_smoke_<timestamp>.json`
- `results/live_smoke_<timestamp>.md`

Markdown is formatted for quick pasting into GitHub issues.

## Interpreting failures

- `FAIL`: site logic ran but one or more steps failed (no videos, bad parse, playback not resolved)
- `ERROR`: module import or subprocess error
- `SKIP`: step not applicable (for example, no categories/search function on that site)

Use this report to pick parser fixes first, then re-run only those sites.
