# Opt-In Diagnostic Telemetry Design

## Goal

Give the maintainer actionable visibility into Cumination failures that occur on
Kodi streaming devices, including Python exceptions, site/listing failures,
resolver failures, and failures that happen after a stream is handed to Kodi.
Reports will appear as grouped issues in a hosted GlitchTip project with email
alerts.

Diagnostic reporting is disabled by default. No diagnostic event or persistent
installation identifier is created until the user explicitly enables reporting
in the add-on settings.

## Non-goals

- Capture general Kodi activity or playback started outside Cumination.
- Upload the Kodi log, page bodies, media titles, search terms, or full URLs.
- Add performance tracing, session replay, analytics, or user profiling.
- Replace the existing Kodi log and Kodi Logfile Uploader workflow.
- Build or operate a custom telemetry dashboard or ingestion service.

## Selected approach

Cumination will send Sentry-compatible error events directly to a hosted
GlitchTip project. A small in-repository reporter will construct and submit the
events through the `requests` dependency already declared by the add-on. The
official Sentry Python SDK will not be bundled, keeping the installation small
and avoiding another runtime dependency on constrained Kodi devices.

The GlitchTip DSN is a project intake credential, not a dashboard credential.
It may be distributed with the add-on and therefore must be treated as public:
it can be extracted and used to forge intake events. Client-side limits protect
against accidental floods from genuine installations, while GlitchTip project
quotas and server-side filtering protect the hosted project. The DSN must be
rotatable in a normal add-on release without changing the event schema.

## User controls

The add-on settings will add a diagnostics section containing:

- **Enable diagnostic reporting**, a boolean that defaults to `false`.
- A short disclosure explaining what is sent and that the ingestion service
  necessarily observes the source IP while accepting an HTTPS request.
- **Send test report**, available only while reporting is enabled. It sends a
  synthetic event and displays either its event ID or a concise delivery error.

Enabling reporting creates a random installation identifier. Disabling it takes
effect immediately and deletes the local report queue, playback context, rate
limit state, and installation identifier. Re-enabling therefore starts with a
new identifier.

## Components

### Telemetry reporter

`resources/lib/telemetry.py` will own the complete reporting boundary:

- opt-in checks;
- event construction and schema validation;
- sanitization;
- stable issue fingerprinting;
- queue persistence and bounds;
- rate limiting and success sampling;
- Sentry envelope serialization;
- short-timeout HTTPS delivery; and
- queue cleanup when reporting is disabled.

Callers pass structured fields to this module. They do not construct raw
GlitchTip payloads or perform their own redaction.

### Diagnostic context

A short-lived context describes the current add-on operation. It contains an
attempt ID, site identifier, operation, start time, and structured network,
resolver, or playback attributes. Supported operations are `listing`, `search`,
`resolve`, and `playback`.

The current context is available in memory during a plugin invocation. Playback
handoff also writes a sanitized, expiring context to the add-on profile
directory so the service process can associate later Kodi player callbacks with
the correct Cumination attempt. Atomic replacement prevents the service from
reading a partially written file. Contexts expire automatically and are
ignored after expiry.

### Playback monitor service

The add-on will declare a lightweight `xbmc.service` entry backed by
`service.py`. The service registers an `xbmc.Player` callback listener and runs
an abort-aware monitor loop. It only observes a playback attempt when a valid,
unexpired Cumination context exists. All unrelated Kodi playback is ignored.

The service also drains queued events. Network delivery therefore does not need
to delay a short-lived plugin invocation.

### Integration points

The initial integration will cover common boundaries rather than adding custom
reporting code to every site module:

- top-level URL dispatch for uncaught exceptions;
- common HTTP helpers for transport and HTTP failures;
- listing completion for an unexpected zero-item result;
- `VideoPlayer` and ResolveURL handoff for extraction and resolver failures; and
- the playback monitor for post-handoff Kodi outcomes.

Explicit structured reporting can be added to a site module later when a site
has a failure mode that cannot be classified at a shared boundary.

The existing extended local exception logger remains in place. Telemetry uses a
separate safe traceback formatter and never transmits captured frame locals.

## Event model

Every event has a UUID event ID, UTC timestamp, level, release, environment,
message, fingerprint, tags, structured contexts, optional sanitized exception,
and bounded breadcrumbs.

Common tags and contexts include:

- add-on version;
- Kodi, Python, and ResolveURL versions where available;
- operating system, CPU architecture, and device class where Kodi exposes it;
- random installation identifier;
- site and operation;
- failure stage and classification;
- elapsed time;
- HTTP method, response status, destination domain, and redirect domains;
- resolver name and outcome;
- stream protocol/container, manifest type, and inputstream usage; and
- playback attempt ID, startup duration, and player outcome.

The initial event types are:

### `addon_exception`

An uncaught Python exception. It includes the exception type, sanitized message,
source-relative stack frames, failing function and line, and recent diagnostic
breadcrumbs. It does not include frame local variables.

### `site_load_failure`

A DNS, TLS, connection, timeout, redirect, HTTP, challenge/block-page, or
unexpected-empty-listing failure. Empty results are only failures when a site
listing request succeeded and the normal listing parser produced zero items.
Empty search results and categories that may legitimately be empty are not
reported.

### `resolve_failure`

No source found, unsupported host, resolver exception, malformed stream URL, or
failed handoff. It records the resolver and sanitized host/protocol chain, but
not the media URL.

### `playback_failure`

Kodi explicitly reports a playback error, the attempted item does not reach an
AV-started callback before the startup timeout, or playback ends during the
early-failure window. An early stop is labeled `probable_failure`, not a certain
failure, because Kodi cannot always distinguish a user stop from a transport
failure.

### `playback_success`

Playback remains active beyond the stability threshold. Success events are
sampled and rate-limited. They provide the denominator needed to distinguish an
unused site from a consistently failing site without turning the feature into
general usage analytics.

## Playback state model

A playback attempt moves through these states:

1. `pending` when Cumination hands a stream to Kodi;
2. `started` when Kodi reports that audio/video has started;
3. `stable` after the stability threshold;
4. `failed` on an explicit player error or startup timeout;
5. `probable_failure` when playback stops inside the early-failure window; or
6. `completed`/`stopped` after stable playback, with no failure event.

Only one terminal outcome is emitted for an attempt. Duplicate or out-of-order
callbacks are idempotent. A normal user stop after stable playback never creates
a failure. Thresholds will be named constants with conservative defaults and
unit tests around their boundary values.

## Privacy and sanitization

All fields pass through one recursive allowlist-based sanitizer immediately
before queueing and again before transmission. Unknown fields are dropped.

The sanitizer removes or transforms:

- URL paths, query strings, fragments, and embedded credentials, retaining only
  scheme when relevant and normalized domain;
- authorization, proxy authorization, cookie, set-cookie, and other secret
  headers;
- passwords, tokens, session IDs, API keys, PINs, and all known authentication
  settings;
- search text, media titles, room/model names, and user/account identifiers;
- response/request bodies and HTML or manifest content;
- local absolute paths and OS usernames, rewriting known source paths relative
  to the add-on root; and
- high-cardinality arbitrary values that are not part of the schema.

Exception messages and breadcrumbs receive secret-pattern and URL scrubbing in
addition to their allowlists. Values have per-field length limits. Events have
a hard serialized-size cap. A report that cannot be made safe or valid is
dropped locally and noted only in the Kodi log.

The reporter does not intentionally collect IP addresses. The hosted service
will necessarily observe the network source IP during HTTPS delivery and may
handle it according to its own service policy; the in-event payload contains no
IP field.

## Breadcrumbs

The reporter keeps a small in-memory ring of structured diagnostic breadcrumbs
for the current invocation or playback attempt. Allowed breadcrumb categories
are operation transition, network outcome, parser outcome, resolver outcome,
and player transition. Breadcrumbs contain timestamps, durations, domains,
status codes, counts, and classifications only. Raw log lines, request/response
bodies, titles, searches, and URLs are never copied into the breadcrumb ring.

## Grouping and alert quality

Failures receive a stable fingerprint composed from the event type, site,
operation/stage, exception class or failure classification, resolver when
applicable, and top in-add-on stack location. Volatile values such as device ID,
message text, line URL, timestamp, and HTTP query data are excluded. This lets
GlitchTip group repeated instances of the same defect while separating failures
that need different fixes.

The client sends all distinct failures while enabled, then suppresses repeats
of the same fingerprint within a cooldown window. It retains a suppressed count
and includes that count with the next permitted event. Playback successes use a
low deterministic sample and their own stricter rate limit. Limits are enforced
per installation and globally per time window.

Because the DSN is public, server-side quotas will also cap total project
ingestion. Events will carry a fixed logger/source tag so obvious forged or
malformed traffic can be filtered without trusting the installation identifier.

GlitchTip project alerts will initially notify by email for new issues and for a
recurrence after a resolved issue. Frequency-based alert tuning can be added
after observing real traffic.

## Queue and delivery behavior

Sanitized events are stored in a capped queue under the add-on profile
directory. Queue writes are atomic. Limits apply to event count, total bytes,
event age, and retry attempts. When full, the oldest sampled success is removed
first, followed by the oldest event if necessary.

The service sends small batches with short connection and response timeouts.
Transient network and server failures use capped exponential backoff with
jitter. Permanent client errors drop the affected event and log a sanitized
reason locally. Delivery never raises into listing, resolving, or playback code.

The service checks the opt-in flag before reading, queueing, and sending. If the
flag becomes false, it performs local telemetry cleanup and makes no network
request. Kodi shutdown uses a bounded final flush only if it can complete
without delaying shutdown; otherwise the queue remains for the next start.

## Failure isolation

Every public telemetry entry point is best-effort and exception-safe. A bug in
serialization, storage, sanitization, player monitoring, or delivery must not
change add-on output, suppress the original exception, prevent playback, or
display repeated dialogs. Internal telemetry failures go only to the Kodi log
with secrets scrubbed.

The monitor sleeps through Kodi's abort-aware API and exits promptly on abort.
It performs no polling or network work when reporting is disabled and no queue
exists.

## Test strategy

### Unit tests

- reporting is inert with the default disabled setting;
- enable, disable, identifier lifecycle, and immediate cleanup;
- recursive allowlisting and redaction of credentials, headers, URLs, local
  paths, authentication settings, exception messages, and breadcrumb values;
- payload size and field-length limits;
- stable fingerprints and suppressed-count behavior;
- success sampling and global/per-fingerprint rate limits;
- atomic queue operations, bounds, expiry, retry limits, and eviction order;
- Sentry envelope shape and DSN parsing;
- transient versus permanent delivery failures;
- operation context creation and expiry;
- empty listing classification versus valid empty search/category results; and
- all playback state transitions, duplicate callbacks, time boundaries, normal
  stops, unrelated playback, and shutdown.

All network, clock, filesystem, settings, and Kodi player interactions will be
mocked in unit tests.

### Integration tests

- top-level dispatch captures and re-raises/logs an uncaught exception without
  changing existing behavior;
- HTTP and resolver boundaries produce the expected structured event;
- a playback handoff is correlated with callbacks in the service process;
- the service drains queued envelopes to a mock GlitchTip endpoint; and
- telemetry failures do not affect directory completion or playback handoff.

### Manual Kodi validation

On a representative streaming device:

1. confirm a default installation makes no telemetry request;
2. enable reporting and deliver a test report;
3. exercise a working site and stable playback;
4. exercise a deliberately invalid stream and a startup timeout;
5. exercise an unavailable or blocked site;
6. trigger a controlled test exception;
7. disconnect networking, create an event, reconnect, and verify retry;
8. play unrelated Kodi media and verify it is ignored; and
9. disable reporting and verify all local telemetry state is removed.

The resulting GlitchTip issues will be inspected for grouping quality,
repairability, and absence of prohibited data before release.

## Rollout and success criteria

The feature will ship disabled. Initial use will be limited to maintainer-owned
devices. It is ready for wider opt-in use when:

- every target failure class creates a grouped, actionable issue;
- playback outcomes correlate only with Cumination attempts;
- the sanitizer tests cover adversarial secret and URL cases;
- disabling reporting causes immediate cleanup and no further requests;
- queue and delivery failures have no visible effect on the add-on; and
- real GlitchTip events contain enough version, site, stage, network, resolver,
  traceback, and player context to reproduce or prioritize a fix without
  exposing prohibited user data.
