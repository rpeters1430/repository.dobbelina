# LemonCams Direct HLS Playback Design

## Goal

Play LemonCams streams using the standard HLS URLs supplied by the LemonCams API instead of routing them through Stripchat's MOUFLON manifest proxy.

## Background

Current LemonCams streams use ordinary HLS playlists hosted on `growcdnssedge.com`. Live inspection confirmed that the master playlist, child playlist, initialization map, and media segments return HTTP 200. These manifests contain neither MOUFLON tags nor placeholder `media.mp4` segments.

The current implementation passes the LemonCams URL into Stripchat playback. Stripchat adds `playlistType=lowLatency`, classifies the result as proxy-required, and rewrites its media requests through a localhost proxy. That proxy intentionally rejects `growcdnssedge.com`, causing playback to begin loading and then fail.

## Design

When `LemonCams.Playvid` receives a cached HLS URL:

1. Create a `VideoPlayer` configured for inputstream.adaptive HLS playback.
2. Play the cached URL directly.
3. Attach URL-encoded `User-Agent`, `Referer`, and `Origin` headers using LemonCams as the origin and referrer.
4. Add `manifest_headers=1` so inputstream.adaptive applies the headers to child playlists and segments.

When no cached stream URL is present:

1. Search the LemonCams API for the exact provider and username.
2. If found, play the resulting URL through the same direct-HLS path.
3. If no stream is found, notify the user that the model is offline or unavailable.

Stripchat playback and its manifest proxy will not be called by LemonCams.

## Error Handling

- Invalid LemonCams model identifiers retain the existing notification.
- Unsupported providers retain the existing notification.
- Missing or stale streams produce the existing offline/no-stream notification.
- Kodi and inputstream.adaptive remain responsible for reporting transport failures after playback handoff.

## Testing

Focused tests will verify:

- A cached LemonCams HLS URL is passed directly to `VideoPlayer`.
- The playback URL includes LemonCams headers and `manifest_headers=1`.
- An uncached model is refreshed through `_find_model_stream`.
- A missing refreshed stream reports the offline/no-stream notification.
- Stripchat playback is not invoked.

The focused LemonCams and Stripchat test files will run after implementation, followed by the broader relevant site tests if practical.
