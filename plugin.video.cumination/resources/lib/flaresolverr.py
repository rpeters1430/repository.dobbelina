import requests
import time
import os
import uuid
from urllib.parse import urlparse
from kodi_six import xbmc, xbmcaddon
from resources.lib.http_timeouts import HTTP_TIMEOUT_CONNECT, HTTP_TIMEOUT_SHORT

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

        # Preferred path in Kodi runtime.
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
                "Please use 127.0.0.1 or localhost.".format(host)
            )
        else:
            xbmc.log(
                "@@@@Cumination: FlareSolverr configured with non-localhost host '{}'. "
                "Remote access is enabled via 'fs_allow_remote'.".format(host),
                xbmc.LOGWARNING,
            )


class FlareSolverrManager:
    @staticmethod
    def _build_session_id():
        return "cumination_session_{}_{}_{}".format(
            int(time.time() * 1000),
            os.getpid(),
            uuid.uuid4().hex[:8],
        )

    def __init__(self, flaresolverr_url=None, session_id=None):
        self.session = requests.session()
        self.flaresolverr_url = flaresolverr_url or "http://127.0.0.1:8191/v1"
        _validate_flaresolverr_url(self.flaresolverr_url)
        self.session_id = session_id or self._build_session_id()
        self.flaresolverr_session = self.session_id
        self._destroyed = False

        # Only clear old cumination sessions to avoid conflicts with other addons
        self.clear_old_sessions()

        # Try to create session
        self._create_session()

    def _reset_session(self):
        self.session_id = self._build_session_id()
        self.flaresolverr_session = self.session_id
        self._destroyed = False
        self._create_session()

    def _create_session(self):
        session_create_request = {"cmd": "sessions.create", "session": self.session_id}
        try:
            session_create_response = requests.post(
                self.flaresolverr_url,
                json=session_create_request,
                timeout=HTTP_TIMEOUT_CONNECT,
            )
            response_data = session_create_response.json()

            if response_data.get("status") == "error":
                error_msg = str(response_data.get("message", ""))
                if "already exists" in error_msg.lower():
                    self.flaresolverr_session = self.session_id
                else:
                    raise RuntimeError(
                        "Unable to create FlareSolverr session '{}': {}".format(
                            self.session_id, error_msg or "unknown error"
                        )
                    )
            else:
                self.flaresolverr_session = response_data.get(
                    "session", self.session_id
                )
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(
                "Failed to connect to FlareSolverr at {}: {}. "
                "Please check if FlareSolverr is running and configured correctly in addon settings.".format(
                    self.flaresolverr_url, str(e)
                )
            )

    def clear_old_sessions(self):
        """Clear FlareSolverr sessions created by this addon that might have been left over."""
        try:
            # List all sessions
            sessions_list_request = {"cmd": "sessions.list"}
            sessions_list_response = requests.post(
                self.flaresolverr_url,
                json=sessions_list_request,
                timeout=HTTP_TIMEOUT_SHORT,
            )
            sessions = sessions_list_response.json().get("sessions", [])

            # Destroy only our sessions
            for session_id in sessions:
                if session_id.startswith("cumination_session_") and session_id != self.session_id:
                    destroy_request = {"cmd": "sessions.destroy", "session": session_id}
                    requests.post(
                        self.flaresolverr_url,
                        json=destroy_request,
                        timeout=HTTP_TIMEOUT_SHORT,
                    )
        except Exception as e:
            xbmc.log(
                "@@@@Cumination: Failed to clear old FlareSolverr sessions: {}".format(str(e)),
                xbmc.LOGDEBUG,
            )

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
            "session": self.flaresolverr_session,
            "maxTimeout": max_timeout,
        }

        if method.lower() == "post" and post_data:
            flaresolverr_request["postData"] = post_data

        if cookies:
            flaresolverr_request["cookies"] = cookies

        try_count = 0
        while try_count < tries:
            try_count += 1
            try:
                flaresolverr_response = requests.post(
                    self.flaresolverr_url,
                    json=flaresolverr_request,
                    timeout=(max_timeout / 1000) + 10,
                )
                
                status_code = flaresolverr_response.status_code

                if status_code >= 500:
                    response_text = flaresolverr_response.text or ""
                    if "invalid session id" in response_text.lower() and try_count < tries:
                        self._reset_session()
                        flaresolverr_request["session"] = self.flaresolverr_session
                        xbmc.log(
                            "@@@@Cumination: FlareSolverr session expired; recreated session and retrying",
                            xbmc.LOGDEBUG,
                        )
                        continue
                    raise ValueError(
                        "FlareSolverr server error (HTTP {}): {}".format(
                            status_code, response_text[:200]
                        )
                    )

                flaresolverr_response.raise_for_status()
                response_json = flaresolverr_response.json()
                if response_json.get("status") == "error":
                    error_msg = response_json.get("message", "Unknown error")
                    if (
                        "invalid session id" in str(error_msg).lower()
                        and try_count < tries
                    ):
                        self._reset_session()
                        flaresolverr_request["session"] = self.flaresolverr_session
                        xbmc.log(
                            "@@@@Cumination: FlareSolverr session invalid; recreated session and retrying",
                            xbmc.LOGDEBUG,
                        )
                        continue
                    raise ValueError("FlareSolverr error: {}".format(error_msg))

                # Success!
                solution = response_json.get("solution", {})
                
                # Update session cookies from FlareSolverr response
                for cookie in solution.get("cookies", []):
                    self.session.cookies.set(
                        cookie["name"], 
                        cookie["value"], 
                        domain=cookie.get("domain", ""), 
                        path=cookie.get("path", "/")
                    )

                # Return a pseudo-response object that mimics requests.Response
                class MockResponse:
                    def __init__(self, sol):
                        self.text = sol.get("response", "")
                        self.status_code = sol.get("status", 200)
                        self.url = sol.get("url", url)
                        self.headers = sol.get("headers", {})

                    def json(self):
                        import json
                        return json.loads(self.text)

                    def close(self):
                        pass

                return MockResponse(solution)

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
        """Close the FlareSolverr manager and optionally destroy the session."""
        if self._destroyed:
            return

        if destroy_session:
            try:
                destroy_request = {"cmd": "sessions.destroy", "session": self.session_id}
                requests.post(
                    self.flaresolverr_url,
                    json=destroy_request,
                    timeout=HTTP_TIMEOUT_SHORT,
                )
            except Exception as e:
                xbmc.log(
                    "@@@@Cumination: Failed to destroy FlareSolverr session {}: {}".format(
                        self.session_id, str(e)
                    ),
                    xbmc.LOGDEBUG,
                )

        self.session.close()
        self._destroyed = True
