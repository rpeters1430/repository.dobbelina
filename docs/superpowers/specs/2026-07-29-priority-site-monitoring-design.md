# Priority Site Monitoring Design

## Purpose

The existing daily smoke report overstates site health because it primarily
proves that site adapters executed and emitted callbacks. It can report a site
as passing when listings are empty or incorrect, playback is skipped, or a
captured playback URL does not contain usable media.

This design adds a high-confidence monitor for priority sites while retaining
the current broad smoke scan as a lower-confidence coverage signal.

## Goals

- Detect incorrect listings that would make a site unusable in the addon.
- Detect playback URLs that resolve syntactically but do not deliver media.
- Exercise the addon-facing dispatcher path and compare it with Kodi-native
  behavior.
- Open or update a GitHub issue on the first failed priority-site run.
- Produce diagnostic evidence that makes failures straightforward to reproduce.
- Preserve the existing broad smoke scan without presenting it as proof of
  end-to-end health.

## Non-Goals

- Guarantee that every non-priority site works end to end.
- Store downloaded media in reports or workflow artifacts.
- Snapshot exact listing titles, which change too frequently to be reliable.
- Replace focused unit and fixture tests for individual site adapters.
- Automatically repair broken site adapters.

## Priority Sites

Strict monitoring initially covers these 17 sites:

- `anybunny`
- `ask4porn`
- `cam4`
- `camsoda`
- `chaturbate`
- `luxuretv`
- `missav`
- `porndig`
- `pornhub`
- `pornkai`
- `spankbang`
- `streamate`
- `thothub`
- `xnxx`
- `xvideos`
- `youporn`
- `yourlesbians`

This is the existing Tier 1 set with `stripchat` removed and `thothub` added.

## Architecture

The daily site-health workflow separates coverage from confidence.

### Broad Coverage Scan

The existing live smoke runner continues to scan every implemented site. Its
results are labeled **basic coverage**. These results remain useful for
discovering import failures, obvious parser failures, and broad changes, but
they do not contribute to the trusted healthy count.

### Strict Priority Monitor

Each priority site runs in an isolated matrix job so one timeout, process
failure, or site-specific problem cannot hide results for other sites. The
strict runner records four required stages:

1. addon listing dispatch;
2. listing validation;
3. detail-page and playback resolution;
4. media verification.

A site is healthy only when every applicable required stage passes. A skipped
required stage is never interpreted as healthy.

### Kodi-Native Verification

A clean headless Kodi profile installs the built addon and its dependencies.
The verifier requests plugin directories through Kodi's interface, captures
the items Kodi receives, and compares their types, URLs, and counts with the
strict runner. It then invokes a sampled playback item and confirms that Kodi
accepts the resolved media path.

Kodi-native verification complements rather than replaces the strict media
probe. The media probe verifies the remote bytes; Kodi verifies that the
packaged addon and runtime expose the expected behavior.

## Health States

The merged report uses these explicit states:

- `HEALTHY`: all applicable required strict stages passed, including the
  Kodi-native check.
- `BROKEN`: a required user-facing behavior failed.
- `BLOCKED`: the monitored environment encountered an access challenge,
  geographic restriction, rate limit, or similar upstream restriction.
- `HARNESS_ERROR`: monitoring infrastructure failed before it could produce a
  trustworthy site result.
- `NOT_TESTED`: no strict result was produced.

A Kodi-native failure overrides a successful harness result. The broad scan
cannot change a strict result to `HEALTHY`.

## Listing Validation

The strict runner executes the site through the addon dispatcher and captures
the entries intended for Kodi. Site-specific thresholds and allowed hosts live
in `config/site_profiles.json`.

Each priority-site profile defines:

- minimum video item count;
- minimum unique-title and unique-URL ratios;
- allowed detail-page and media hosts, including documented third-party hosts;
- expected playback modes;
- whether thumbnails and descriptions are required or advisory;
- any site-specific challenge or error fingerprints;
- whether a stage is genuinely inapplicable.

The validator requires:

- enough actual video items to satisfy the site profile;
- non-empty titles;
- valid HTTP(S) target URLs;
- uniqueness above the configured thresholds;
- playback modes rather than category, login, advertisement, or navigation
  modes mislabeled as videos;
- reachable sampled detail pages;
- HTML detail responses from an allowed host;
- no challenge, login, removal, placeholder, or error-page fingerprint.

The runner also compares item count, unique ratios, thumbnail coverage,
description coverage, item modes, and host distribution with recent successful
runs. Relative degradation is recorded even when an absolute requirement still
passes. Metadata degradation is advisory unless the site profile marks that
field as required.

Exact titles are not snapshotted.

## Playback and Media Validation

For each priority site, the runner selects representative listing items and
invokes their registered playback path. At least one configured sample must
complete the full playback contract; profiles may require more samples for
sites with multiple distinct playback paths.

The validator:

1. requires a resolved HTTP(S) media URL;
2. follows bounded redirects;
3. rejects empty, placeholder, unsupported, or malformed URLs;
4. rejects HTML, challenge, login, and error documents masquerading as media;
5. parses HLS master and media playlists when returned;
6. parses DASH manifests when returned;
7. fetches one small media segment or bounded byte range;
8. verifies status, content type, and a media-compatible response signature.

The validator records response metadata and a bounded diagnostic excerpt when
safe. It never stores the media segment.

## Results and Diagnostics

Each strict site result includes:

- final health state;
- per-stage state, message, and elapsed time;
- listing count and uniqueness metrics;
- thumbnail and description coverage;
- sampled page and media hosts;
- HTTP status, content type, redirect count, and media kind;
- sanitized addon notifications and exception details;
- failure classification and stable failure signature;
- Kodi-native comparison results;
- a focused local reproduction command.

Secrets, cookies, query tokens, and other sensitive URL values are redacted
before reports, logs, or issues are written. Downloaded media is discarded.

The daily job summary leads with strict priority-site results. Broad coverage
appears in a separate section and is explicitly labeled lower confidence.

## GitHub Issue Lifecycle

Each priority site has one stable issue identity, for example
`[Site Monitor] pornhub is broken`.

On the first `BROKEN` result, automation immediately creates the issue. A
`BLOCKED` result also creates an issue because the site is unusable from the
monitored environment, but it receives a distinct access-blocking label.

The issue contains:

- failed stage and classification;
- current listing-quality metrics and baseline changes;
- sanitized page and media evidence;
- addon notifications or exception details;
- a reproduction command;
- links to complete workflow artifacts.

Subsequent failures update the issue only when the stable failure signature
changes. This avoids daily duplicate comments while preserving meaningful
changes.

`HARNESS_ERROR` results update one workflow-level infrastructure issue and do
not create site-specific defects.

After a site passes the complete strict monitor on two consecutive daily runs,
automation adds a recovery note and closes its issue. A new later failure
reopens the stable site issue or creates it again if reopening is unavailable.

## Baselines

The existing `site-health` branch remains the durable report store. Strict
monitor history is stored separately from broad smoke history so a basic smoke
pass cannot overwrite strict evidence.

Only successful strict runs update a site's healthy baseline. Failed, blocked,
incomplete, and harness-error runs remain in history but cannot redefine broken
behavior as normal.

Baseline history is bounded. It retains enough recent outcomes to calculate
consecutive recovery runs and relative metric changes without growing the
branch indefinitely.

## Error Handling

- A priority site timeout produces a site result rather than terminating its
  matrix chunk.
- An unavailable monitoring dependency produces `HARNESS_ERROR`.
- DNS, rate limiting, geographic restrictions, and challenge pages produce
  `BLOCKED` when positively identified; they are not silently skipped.
- Unclassified user-visible failures default to `BROKEN`, not healthy.
- Missing or malformed site profiles fail validation before the daily monitor
  starts.
- Failure in report merging or issue automation fails the report job visibly
  and updates the workflow-level infrastructure issue when possible.

## Test Strategy

### Listing Validator Tests

Fixtures cover:

- healthy video listings;
- empty listings;
- navigation entries emitted as videos;
- duplicate title or URL floods;
- invalid URLs and disallowed hosts;
- login, challenge, removal, and error pages;
- absolute and relative baseline degradation;
- advisory versus required metadata.

### Media Validator Tests

Fixtures and local HTTP handlers cover:

- direct media responses;
- HLS master and media playlists;
- DASH manifests;
- redirects and redirect limits;
- byte-range responses;
- expired links;
- unsupported content;
- HTTP 200 HTML error and challenge pages;
- malformed manifests and missing media segments.

### Runner Integration Tests

Controlled fake site modules verify:

- dispatcher capture;
- listing and playback stage composition;
- per-stage and per-site timeouts;
- Kodi comparison handling;
- strict health-state precedence;
- report generation and redaction.

### Issue-State Tests

Tests verify:

- issue creation on the first failure;
- stable issue identity;
- updates only when the failure signature changes;
- distinct blocked and infrastructure handling;
- recovery counting;
- closure after two consecutive strict passes;
- later regression handling.

Existing smoke tests remain in place to protect broad-scan behavior.

## Rollout

1. Add strict profile fields and validation for the adjusted 17 priority sites.
2. Implement and test listing and media validators independently.
3. Integrate strict site execution and report generation.
4. Add issue lifecycle automation and tests.
5. Add Kodi-native verification using a clean packaged-addon environment.
6. Run the complete workflow manually against current production behavior and
   classify any monitoring infrastructure failures.
7. Enable the daily strict schedule and immediate issue creation.
8. Promote additional sites into strict monitoring only by adding complete
   profiles; never weaken the health contract to increase the passing count.

## Success Criteria

- The trusted healthy count includes only strict priority-site successes.
- A priority site with empty or structurally incorrect listings is not healthy.
- A priority site whose resolved URL cannot deliver a valid manifest and media
  segment is not healthy.
- A Kodi/runtime mismatch cannot be hidden by a harness pass.
- The first failed daily run opens or updates an actionable issue.
- Temporary recovery does not close an issue until two complete strict passes.
- Reports contain enough sanitized evidence to reproduce and classify failures
  without storing media.
