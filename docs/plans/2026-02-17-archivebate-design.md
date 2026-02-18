# Archivebate Site Plugin — Design

**Date**: 2026-02-17
**Status**: Approved
**Reference**: `docs/sites/ARCHIVEBATE_ANALYSIS.md`

---

## Summary

Add Archivebate (cam-archive site) as a new Cumination site plugin. The site runs on
Laravel + Livewire. Video pages are fully server-rendered; listing pages require a
two-step Livewire fetch (GET for session/CSRF, POST for video fragment).
Videos are hosted on MixDrop — ResolveURL handles playback with no custom work.

---

## Architecture

### Files

| File | Action |
|---|---|
| `plugin.video.cumination/resources/lib/sites/archivebate.py` | Create |
| `plugin.video.cumination/resources/lib/sites/__init__.py` | Add `'archivebate'` to `__all__` |
| `tests/fixtures/sites/archivebate_list.html` | Create (saved Livewire fragment) |
| `tests/fixtures/sites/archivebate_video.html` | Create (saved `/watch/NNNNNN` page) |
| `tests/sites/test_archivebate.py` | Create |

### Module structure

```
Main()           → add platform dirs + call List(site.url)
List(url)        → _livewire_list(url) → parse fragment → add_download_link() × N
Playvid(url)     → getHtml() → select iframe.video-frame → play_from_link_to_resolve()
_livewire_list() → private helper: GET→CSRF→POST, returns HTML fragment
```

---

## HTTP Layer

**Choice**: `requests.Session` (per call, not module-level).

Rationale: Livewire requires a correlated session cookie + CSRF token header. The
shared `utils` cookie jar (`cj`) is global and could bleed between sites; `postHtml`
is cached which breaks dynamic Livewire responses. Two existing sites (hdporn92,
pornhoarder) already import `requests` directly — this is an established pattern.

### Two-step fetch

1. `session.get(url)` — receives `archivebate_session` + `XSRF-TOKEN` cookies,
   extracts CSRF token from `<meta name="csrf-token">` and Livewire component state
   from `wire:initial-data` attribute.
2. `session.post('/livewire/message/<component>', json=payload, headers={X-CSRF-TOKEN, X-Livewire})` —
   returns JSON with `effects.html` (the video fragment) and `serverMemo`.

---

## Site Functions

### `Main()`

Adds platform directories then calls `List(site.url)`:

| Directory | URL |
|---|---|
| Chaturbate | `https://archivebate.com/platform/Y2hhdHVyYmF0ZQ==` |
| Stripchat | `https://archivebate.com/platform/c3RyaXBjaGF0` |

### `List(url)`

Calls `_livewire_list(url)`, parses the returned HTML fragment:

| Field | Selector | Attr |
|---|---|---|
| Watch URL | `a[href*="/watch/"]` | `href` (absolute) |
| Thumbnail | `video.video-splash-mov` | `poster` |
| Performer name | `a[href*="/profile/"]` | `.text.strip()` |

No pagination in v1 (36 items per Livewire call). Pagination tracked as a TODO.

### `Playvid(url, name, download=None)`

Plain `utils.getHtml(url, site.url)` — page is server-rendered. Extracts MixDrop
embed URL from `iframe.video-frame[src]` and passes to `play_from_link_to_resolve()`.

---

## Testing

- No live network calls — mock `requests.Session` in tests.
- `archivebate_list.html`: saved Livewire HTML fragment (36 items).
- `archivebate_video.html`: saved `/watch/NNNNNN` page with MixDrop iframe.
- Tests verify: correct item count, URL/thumb/name extraction, iframe src extraction.

---

## Known Limitations / Future Work

- **Pagination**: Livewire `loadMore` XHR pattern not yet confirmed. Needs one sniff
  session (scroll to bottom, capture XHR). Add as follow-up.
- **Other platforms**: Camsoda, OnlyFans, TikTok platform URLs not yet confirmed.
- **MixDrop availability**: Requires ResolveURL MixDrop resolver to be enabled by user.
