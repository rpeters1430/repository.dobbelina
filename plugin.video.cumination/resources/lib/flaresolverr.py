import requests
import time
from urllib.parse import urlparse
from kodi_six import xbmc, xbmcaddon

_ALLOWED_FS_SCHEMES = ("http", "https")
_LOCALHOST_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _validate_flaresolverr_url(url):
    """Raise ValueError if url is not a safe FlareSolverr endpoint."""
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Invalid FlareSolverr URL: {}".format(url))
    if parsed.scheme not in _ALLOWED_FS_SCHEMES:
        raise ValueError(
            "FlareSolverr URL must use http or https, got: {}".format(parsed.scheme)
        )
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("FlareSolverr URL has no host: {}".format(url))
    if host not in _LOCALHOST_HOSTS:
        allow_remote = False

        # Automatically allow private/local/Tailscale IPs and domains
        try:
            import ipaddress
            # Strip brackets for IPv6 addresses if present
            ip_str = host.strip("[]")
            ip = ipaddress.ip_address(ip_str)
            is_tailscale = ip.version == 4 and ip in ipaddress.ip_network("100.64.0.0/10")
            if ip.is_private or ip.is_loopback or ip.is_link_local or is_tailscale:
                allow_remote = True
        except ValueError:
            # Check for local, LAN, or Tailscale domain names
            if host.endswith(".local") or host.endswith(".lan") or host.endswith(".ts.net") or host.endswith(".tailnet"):
                allow_remote = True

        # Preferred path in Kodi runtime.
        if not allow_remote:
            try:
                if (
                    hasattr(xbmc, "getAddonSettings")
                    and hasattr(xbmc, "getAddonId")
                    and xbmc.getAddonSettings(xbmc.getAddonId()).getSetting("fs_allow_remote")
                    == "true"
                ):
                    allow_remote = True
            except Exception:
                pass

        # Backward-compatible fallback for environments without xbmc.getAddonSettings.
        if not allow_remote:
            try:
                if xbmcaddon.Addon().getSetting("fs_allow_remote") == "true":
                    allow_remote = True
            except Exception:
                pass

        # Non-Kodi test/harness environments may not expose addon settings APIs.
        # Allow remote hosts there to preserve existing tooling behavior.
        if not allow_remote and not (
            hasattr(xbmc, "getAddonSettings") or hasattr(xbmcaddon, "Addon")
        ):
            allow_remote = True

        if not allow_remote:
            raise RuntimeError(
                "FlareSolverr is configured with a remote host '{}'. "
                "For security, only localhost is allowed by default. "
                "Please use 127.0.0.1 or localhost, or enable remote "
                "FlareSolverr hosts in addon settings.".format(host)
            )
        else:
            xbmc.log(
                "@@@@Cumination: FlareSolverr configured with non-localhost host '{}'. "
                "Remote access is enabled via 'fs_allow_remote'.".format(host),
                xbmc.LOGWARNING,
            )


class FlareSolverrManager:
    def __init__(self, flaresolverr_url=None, session_id=None):
        self.session = requests.session()
        self.flaresolverr_url = flaresolverr_url or "http://127.0.0.1:8191/v1"
        _validate_flaresolverr_url(self.flaresolverr_url)
        self.session_id = session_id
        self.flaresolverr_session = None
        self._destroyed = False

    def request(self, url, method="get", post_data=None, tries=3, max_timeout=60000):
        """Proxy a request through FlareSolverr."""
        if self._destroyed:
            raise RuntimeError("FlareSolverrManager has been destroyed")

        # Handle cookies from the requests session if any
        cookies = []
        for cookie in self.session.cookies:
            cookies.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
            })

        flaresolverr_request = {
            "cmd": "request.get" if method.lower() == "get" else "request.post",
            "url": url,
            "maxTimeout": max_timeout,
        }

        if method.lower() == "post" and post_data:
            flaresolverr_request["postData"] = post_data

        if cookies:
            flaresolverr_request["cookies"] = cookies

        xbmc.log(
            "@@@@Cumination: [CF-DIAG] FlareSolverr request: cmd={} url={} "
            "session={} maxTimeout={}ms cookies_sent={} tries={}".format(
                flaresolverr_request["cmd"], url, "stateless",
                max_timeout, len(cookies), tries,
            ),
            xbmc.LOGINFO,
        )

        try_count = 0
        while try_count < tries:
            try_count += 1
            attempt_start = time.time()
            try:
                flaresolverr_response = requests.post(
                    self.flaresolverr_url,
                    json=flaresolverr_request,
                    timeout=(max_timeout / 1000) + 10,
                )

                status_code = flaresolverr_response.status_code
                xbmc.log(
                    "@@@@Cumination: [CF-DIAG] FlareSolverr attempt {}/{} for {} "
                    "returned HTTP {} in {:.2f}s".format(
                        try_count, tries, url, status_code, time.time() - attempt_start
                    ),
                    xbmc.LOGINFO,
                )

                if status_code >= 500:
                    response_text = flaresolverr_response.text or ""
                    raise ValueError(
                        "FlareSolverr server error (HTTP {}): {}".format(
                            status_code, response_text[:200]
                        )
                    )

                flaresolverr_response.raise_for_status()
                response_json = flaresolverr_response.json()
                if not isinstance(response_json, dict):
                    response_json = {}

                if response_json.get("status") == "error":
                    error_msg = response_json.get("message", "Unknown error")
                    xbmc.log(
                        "@@@@Cumination: [CF-DIAG] FlareSolverr returned status=error "
                        "on attempt {}/{}: {}".format(try_count, tries, error_msg),
                        xbmc.LOGWARNING,
                    )
                    raise ValueError("FlareSolverr error: {}".format(error_msg))

                # Success!
                solution = response_json.get("solution") or {}
                if not isinstance(solution, dict):
                    solution = {}
                
                # Update session cookies from FlareSolverr response
                for cookie in solution.get("cookies") or []:
                    if isinstance(cookie, dict) and "name" in cookie and "value" in cookie:
                        self.session.cookies.set(
                            cookie["name"], 
                            cookie["value"], 
                            domain=cookie.get("domain") or "", 
                            path=cookie.get("path") or "/"
                        )

                # Return a pseudo-response object that mimics requests.Response
                class MockResponse:
                    def __init__(self, sol, raw_json=None):
                        self.text = sol.get("response", "")
                        self.status_code = sol.get("status", 200)
                        self.url = sol.get("url", url)
                        self.headers = sol.get("headers", {})
                        self.raw_json = raw_json

                    def json(self):
                        import json

                        return json.loads(self.text)

                    def close(self):
                        pass

                return MockResponse(solution, raw_json=response_json)

            except (requests.exceptions.RequestException, ValueError) as e:
                if try_count >= tries:
                    raise
                xbmc.log(
                    "@@@@Cumination: FlareSolverr request failed (attempt {}/{}): {}".format(
                        try_count, tries, str(e)
                    ),
                    xbmc.LOGDEBUG,
                )
                time.sleep(1)

        raise RuntimeError("FlareSolverr request failed after {} attempts".format(tries))

    def close(self, destroy_session=False):
        """Close the local HTTP session."""
        if self._destroyed:
            return

        self.session.close()
        self._destroyed = True
