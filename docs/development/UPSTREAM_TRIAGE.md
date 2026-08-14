# Upstream Triage Report

Generated: 2026-08-13
Pending commits: 6 (grouped into 6 items)

Run `python scripts/sync_manager.py` (interactive) to review/cherry-pick, or `python scripts/sync_manager.py --report` to regenerate this file.

## New Sites Available (0)

Sites touched by these commits don't exist in our fork yet. Candidates for new site modules.

_None._

## Needs Review (2)

Touches a site we have that isn't BeautifulSoup-migrated, or mentions playback/decrypt - worth reviewing for porting.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| #1929 | `736f5558` | camwhorestv | - |  | camwhorestv - fixes #1929 |
| b541d614 | `b541d614` | stripchat | - |  | Stripchat - Show/Hide model info for increased loadin speed |

## Likely Already Covered (2)

Only touches BeautifulSoup-migrated sites we already have - spot-check, likely skip.

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| #1928 | `140dc06a` | chaturbate | - |  | chaturbate - fixes #1928 |
| #1926 | `618f068f` | archivebate, chaturbate | - |  | archivebate, chaturbate - fixes #1926 fixes #1927 fixes #1799 fixes #1140 |

## Auto-Skip (2)

No site module changes detected (changelog/icon/docs/version-bump-style commits).

| Group | Commits | Sites | New Sites | Playback | Message(s) |
|---|---|---|---|---|---|
| 0d16ac45 | `0d16ac45` | - | - |  | Add files via upload |
| 6e08f6b6 | `6e08f6b6` | - | - |  | Additional images for site |
