# Chaturbate and KissJav Playback Fix Design

## Goal

Restore Chaturbate playback when room-page JavaScript no longer exposes the room dossier, and correct KissJav media request referrers.

## Design

Chaturbate will continue to parse `initialRoomDossier` first so all existing proxy, credential, and play-mode behavior remains unchanged. When that data is absent, `Playvid` will call Chaturbate's `get_edge_hls_url_ajax/` endpoint with the room slug and AJAX request headers. A public-room HLS URL becomes a minimal fallback stream for the existing InputStream/proxy flow; modes needing dossier-only fields remain unchanged.

KissJav will send `site.url` as the direct-media referer rather than the individual video-page URL.

## Validation

Add unit tests for the Chaturbate AJAX fallback and KissJav referer. Run the focused test modules, then the live smoke checks for both sites.
