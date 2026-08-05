# Site Monitor Accuracy and Triage Repair Design

## Purpose

The strict site monitor currently creates misleading site issues when its
headless harness cannot reproduce Kodi playback behavior, when navigation
directories are counted as video listings, or when an unresolved detail-page
URL is probed as media. The workflow also creates duplicate issues because it
does not provide existing GitHub issues to the triage generator.

This design repairs those monitor and issue-lifecycle defects without weakening
the strict health contract defined by the priority-site monitoring design.

## Confirmed Failure Modes

- Ask4Porn is blocked upstream. Both `ask4porn.cc` and `tap4porn.cc` return HTTP
  403 after FlareSolverr challenge processing. This is a listing-stage access
  block, not a playback defect.
- PornKai can emit third-party hosted embeds. The harness currently echoes an
  unresolved embed page as if it were resolved media, producing a false
  `HTML_PAYLOAD` result.
- XNXX can select a removed or transient first listing item. When playback does
  not resolve, the strict evaluator substitutes the detail-page sample URL and
  incorrectly probes HTML as media.
- YouPorn can return navigation and category entries without video entries on a
  GitHub runner. Those directories are counted as listing samples, allowing the
  listing contract to pass before playback is reported as skipped.
- The workflow never passes `--existing-issues` to the triage generator, so
  recurring failures create duplicate issues instead of updating or reopening
  the stable site issue.

## Goals

- Validate only emitted video/download entries as listing samples.
- Preserve the distinction between listing, playback, media, access-blocking,
  and harness failures.
- Probe media only when the playback stage produced a resolved playback URL.
- Resolve direct media embedded in hosted pages when the generic harness can do
  so; otherwise report a harness limitation instead of a site access block.
- Reuse the stable GitHub issue for each monitored site.
- Keep Ask4Porn's single issue open as `BLOCKED` until two complete healthy runs.
- Close the confirmed false-positive or duplicate issues for PornKai, XNXX, and
  YouPorn after the repaired behavior is covered by tests.

## Non-Goals

- Add `tap4porn.cc` as an alternate domain; it has the same HTTP 403 behavior.
- Add proxy rotation, CAPTCHA services, or a new browser automation stack.
- Weaken playback or media requirements to make strict results pass.
- Repair unrelated site adapters or refactor the full smoke-test harness.

## Design

### Listing Capture

`live_smoke_test.py` will keep navigation directories and downloadable video
items in their existing separate capture collections. Only downloadable video
items will be copied into `listing_samples`. Directory entries may still drive
the list, categories, and search probes, but they cannot satisfy the strict
listing contract.

This makes an empty Ask4Porn or YouPorn video listing fail at the listing stage
even when `Main` emitted search, category, or filter directories.

### Playback and Media Evaluation

`strict_site_monitor.py` will use `play.play_url` as the sole media-validation
input. `play.sample_url` remains diagnostic evidence for the selected detail
page and is never treated as media.

Evaluation precedence will follow user-visible data flow:

1. positively identified access block;
2. invalid video listing;
3. failed or skipped required playback;
4. failed media verification;
5. healthy result.

A FlareSolverr notification reporting a website HTTP 403, an unresolved
challenge, or an equivalent access denial will produce `BLOCKED` at the
listing stage. Missing monitoring infrastructure remains `HARNESS_ERROR`.

### Hosted Embed Handling

The fake `VideoPlayer` used by the live harness will not treat a hosted page
URL as resolved media merely because ResolveURL would normally receive it. For
HTTP(S) string sources, it will fetch the hosted page and reuse the harness's
bounded direct MP4/HLS extraction. A discovered direct URL is captured as
playback. If no direct URL can be extracted, the play step records a clear
harness limitation rather than a successful playback URL.

The implementation remains generic and does not special-case PornKai or a
particular host domain.

### GitHub Issue Reuse

Before generating triage requests, the report job will fetch existing
site-monitor issues with their number, title, body, and state into JSON. It will
pass that file through the generator's existing `--existing-issues` interface.

The existing marker `<!-- strict-site-health:<site> -->` remains the stable
identity. An open issue with the same signature receives no action, a changed
signature updates the issue, and a closed issue is reopened. The workflow must
not create a second open issue for the same marker.

### Existing Issue Disposition

- Keep Ask4Porn #279 open and describe it as a confirmed listing-stage access
  block.
- Close PornKai #276 and duplicate #280 as monitor/harness false positives.
- Close XNXX #281 as a transient sample plus media-fallback false positive.
- Close YouPorn #282 as a runner-dependent listing failure that was mislabeled
  as playback.

Each closure will receive a concise diagnostic comment. No issue will claim the
underlying site was repaired when only monitor behavior was corrected.

## Error Handling

- A website HTTP 403 returned through a functioning FlareSolverr service is
  `BLOCKED`, not infrastructure failure.
- A connection failure to the configured FlareSolverr service is
  `HARNESS_ERROR` for a site that requires it.
- A required playback stage without a resolved URL is `BROKEN` unless evidence
  positively identifies an upstream block or harness limitation.
- Media validation is not attempted without a resolved playback URL.
- Failure to fetch existing issues must fail the report job rather than silently
  reverting to duplicate issue creation.

## Test Strategy

Unit tests will prove each regression before production changes:

- directory-only output fails the listing contract;
- downloadable entries remain valid listing samples;
- a skipped playback page is not probed as media;
- media failure is reported only after successful playback resolution;
- FlareSolverr website HTTP 403 evidence becomes listing-stage `BLOCKED`;
- an unreachable required FlareSolverr service remains a harness limitation;
- hosted page resolution captures an embedded direct MP4/HLS URL and does not
  report the hosted HTML page as media;
- existing open issues suppress duplicate creation;
- existing closed issues are reopened;
- the workflow passes fetched existing-issue JSON to the generator.

The narrow runner, strict-monitor, triage-generator, and workflow tests will run
first, followed by the complete Python test suite when practical.

## Success Criteria

- Ask4Porn produces one listing-stage `BLOCKED` issue for its confirmed HTTP
  403 response.
- Directory-only listings cannot pass strict validation.
- A detail or embed HTML page cannot be reported as a resolved media URL.
- PornKai and XNXX are not labeled blocked solely because the harness received
  HTML from an unresolved playback page.
- Every site marker has at most one open monitor issue after a report run.
- The authorized obsolete issues are closed with accurate comments.

