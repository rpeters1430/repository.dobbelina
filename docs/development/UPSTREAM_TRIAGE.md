# Upstream Triage Report

Generated: 2026-07-30
Pending commits: 6 (grouped into 6 items)

Run `python scripts/sync_manager.py` (interactive) to review/cherry-pick, or `python scripts/sync_manager.py --report` to regenerate this file.

## New Sites Available (0)

Sites touched by these commits don't exist in our fork yet. Candidates for new site modules.

_None._

## Needs Review (4)

Touches a site we have that isn't BeautifulSoup-migrated, or mentions playback/decrypt - worth reviewing for porting.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 945df145 | `945df145` | stripchat | - |  | Stripchat - More details about models |
| 4df29b1c | `4df29b1c` | stripchat | - |  | Added status for models not in public streaming |
| cd265578 | `cd265578` | stripchat | - |  | Stripchat - added Top Models |
| #1912 | `6a6957ef` | stripchat | - |  | #1912 Stripchat |

## Likely Already Covered (1)

Only touches BeautifulSoup-migrated sites we already have - spot-check, likely skip.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| #1918 | `4b0b1f44` | eporner, pornez | - |  | fix pornez, eporner length filter #1918 |

## Auto-Skip (1)

No site module changes detected (changelog/icon/docs/version-bump-style commits).

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 4b48f7b0 | `4b48f7b0` | - | - |  | Stripchat fix |
