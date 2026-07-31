# Live Smoke & Strict Priority Site Monitoring

Use `scripts/live_smoke_test.py` for broad site checks and `scripts/strict_site_monitor.py` for trusted priority site monitoring.

## Broad Smoke Check vs Strict Monitoring

1. **Broad Smoke Scan**: Runs all 170 site scrapers across 4 matrix chunks. Reports `PASS`, `WARN`, `FAIL`, `SKIP`.
2. **Strict Priority Site Monitoring**: Runs trusted, contract-based verification against the 17 priority sites (`pornhub`, `xvideos`, `spankbang`, `thothub`, etc.).
   - Validates listing contract (`min_video_items`, title/URL uniqueness, host checks).
   - Validates media stream bytes (direct media, HLS playlists, DASH manifests).
   - Tracks 14-run history, failure signatures, and requires **2 consecutive healthy passes** before closing GitHub issues.

## Strict Priority Site Commands

Run strict monitoring for a specific site:

```bash
python scripts/strict_site_monitor.py --site pornhub --out results/strict
```

Run Kodi runtime probe via JSON-RPC:

```bash
python scripts/kodi_site_probe.py --site pornhub --out results/kodi
```

Merge strict reports and update history:

```bash
python scripts/strict_health_history.py results/strict/strict_site_*.json --out results
```

Generate strict triage issue actions:

```bash
python scripts/generate_strict_triage_requests.py --latest results/strict_health_latest.json --history results/strict_history.json --out results/strict_triage_requests.json
```

## Important Safety Rules

- Monitoring scripts perform read-only network checks and bounded 64 KiB media reads.
- Query parameters containing sensitive keys (`token`, `auth`, `cookie`, `key`, `signature`, `expires`) are automatically redacted before persistence.
- Media streams are never saved to disk.

## Strict States & Interpretations

- `HEALTHY`: All strict listing, playback, and media contract checks passed cleanly.
- `BROKEN`: One or more required contract checks failed (e.g. parser drop, missing video items, invalid HLS manifest).
- `BLOCKED`: Cloudflare challenge or age-verification wall detected.
- `HARNESS_ERROR`: Infrastructure error, network crash, or Python exception before trustworthy result.
- `NOT_TESTED`: Priority site was omitted from test run.
