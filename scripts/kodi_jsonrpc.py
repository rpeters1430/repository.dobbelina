#!/usr/bin/env python3
"""Transport-only Kodi JSON-RPC client."""

import json
import time
import urllib.error
import urllib.request
from typing import Any


class KodiJSONRPCError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"Kodi JSON-RPC Error {code}: {message}")
        self.code = code
        self.message = message


class KodiClient:
    def __init__(self, url: str = "http://127.0.0.1:8080/jsonrpc", timeout: float = 10.0):
        self.url = url
        self.timeout = timeout
        self._req_id = 1
        self._opener = urllib.request.build_opener()

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self._req_id,
        }
        self._req_id += 1

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                raw_res = resp.read().decode("utf-8")
                res = json.loads(raw_res)

            if "error" in res:
                err = res["error"]
                raise KodiJSONRPCError(
                    code=err.get("code", -1),
                    message=err.get("message", "Unknown error"),
                )
            return res.get("result")

        except urllib.error.HTTPError as exc:
            raise KodiJSONRPCError(code=exc.code, message=f"HTTP Error {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise KodiJSONRPCError(code=-1, message=f"Connection error: {exc.reason}") from exc

    def wait_until_ready(self, timeout: float = 30.0, poll_interval: float = 0.5) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            try:
                res = self.call("JSONRPC.Ping")
                if res == "pong":
                    return True
            except Exception:
                pass
            time.sleep(poll_interval)
        return False
