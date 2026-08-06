# FlareSolverr v1/v2 Compatibility Design

## Context

Cumination currently creates a FlareSolverr session before every solve and
destroys it immediately afterward. FlareSolverr 2.0.0 accepts stateless
`request.get` calls but no longer supports `sessions.create` or
`sessions.destroy`. This prevents sites such as SpankBang from opening even
though the configured FlareSolverr endpoint is healthy.

The observed v2 failure is HTTP 400 during `sessions.create`. A direct
stateless `request.get` to the same endpoint successfully returned the
SpankBang listing with HTTP 200.

## Design

`FlareSolverrManager` will use stateless `request.get` calls for its normal
request path. It will not create a browser session during initialization and
will not send a session identifier in the request payload. Closing a manager
will continue to close its local HTTP session, but it will not call the removed
FlareSolverr session-destruction command.

This is compatible with both supported API generations because FlareSolverr
v1 accepts `request.get` without a session and v2 requires that form. The
manager will continue to process the returned response, cookies, user agent,
status, and error payloads exactly as it does now.

## Compatibility Boundary

- FlareSolverr v1: stateless `request.get` remains supported.
- FlareSolverr v2.0.0: avoids unsupported `sessions.create` and
  `sessions.destroy` commands.
- Existing URL validation, request retry count, timeouts, cookie handling, and
  response wrapper behavior remain unchanged.
- The public constructor keeps accepting `session_id` for source compatibility,
  but normal requests do not depend on or transmit it.

## Error Handling

Transport failures and FlareSolverr `status=error` responses retain the
existing retry and exception behavior. The change removes only session-command
failures; it does not mask genuine solve failures or silently bypass
FlareSolverr.

## Testing

Tests will prove that:

1. Manager construction makes no `sessions.create` request.
2. `request.get` omits the `session` field and accepts a v1-shaped successful
   response.
3. The same request path accepts the observed v2.0.0 successful response.
4. Closing the manager does not send `sessions.destroy`.
5. Existing retries, errors, cookies, and URL-validation tests remain green.

The focused `tests/test_flaresolverr.py` suite will run first, followed by the
relevant SpankBang tests and the broader suite when practical.

## Out of Scope

- Detecting or configuring a FlareSolverr version manually.
- Restoring persistent multi-request browser sessions.
- Changing SpankBang parsing or Cloudflare detection.
- Adding proxies, CAPTCHA services, or another browser stack.
