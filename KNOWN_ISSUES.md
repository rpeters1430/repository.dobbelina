# Known Issues and Technical Debt

## Kodi compatibility and packaging
- `plugin.video.uwc` and `script.video.F4mProxy` still target the legacy `xbmc.python` 2.1.0 interface, which aligns with pre-Matrix Kodi releases and needs to be raised for modern versions.
- `plugin.video.cumination` lacks an explicit `xbmc.python` requirement; it bundles `kodi-six` for Python 2/3 bridging but should declare a modern Python API to signal Matrix/Nexus/Omega support.

## Functional issues observed in testing
- **pornhub** – Search results populate, but returned titles no longer reflect the query string, so searches surface unrelated videos.
- **spankbang** – Tag picker only exposes about two pages of items and search truncates to roughly 20 results even when more exist.
- **hqporner** – Pagination past page 6 intermittently shows "website too slow" errors that require retrying before pages load.
- **naked** – Landing view delays thumbnails, gender tabs never populate, API requests return 500 errors, and no playable streams are exposed.
- **pornone** – Pagination loops back to page 1 after reaching page 5 despite more results being available.
- **anybunny** – Search is blocked by a Cloudflare challenge and pagination sometimes repeats the previous page of results.
- **drtuber** – Search returns only the first ~30 hits before the site rate limits further queries.

## Technical debt
- Multiple add-ons still rely on legacy dependency versions (`xbmc.python` 2.1.0) and outdated repository endpoints, signaling the need for a coordinated compatibility uplift.
- The repository lacks a unified declaration of supported Kodi releases, making it unclear which versions are officially maintained.
