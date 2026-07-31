#!/usr/bin/env python3
"""Kodi runtime site probe via JSON-RPC."""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from scripts.kodi_jsonrpc import KodiClient, KodiJSONRPCError
from scripts.live_smoke_test import get_site_profile


def probe_site(
    client: KodiClient,
    site_name: str,
    strict_record: dict[str, Any] | None = None,
    timeout: float = 15.0,
) -> dict[str, Any]:
    """Probe directory listing and playback in a running Kodi instance via JSON-RPC."""
    profile = get_site_profile(site_name)
    plugin_url = f"plugin://plugin.video.cumination/?mode={site_name}.Main"

    try:
        dir_res = client.call(
            "Files.GetDirectory",
            {
                "directory": plugin_url,
                "media": "files",
                "properties": ["file", "filetype", "label", "thumbnail", "plot"],
            },
        )
    except Exception as exc:
        return {
            "site": site_name,
            "passed": False,
            "item_count": 0,
            "playback_started": False,
            "message": f"Kodi directory fetch error: {type(exc).__name__}: {exc}",
        }

    files = dir_res.get("files", []) if isinstance(dir_res, dict) else []
    item_count = len(files)

    if item_count == 0:
        return {
            "site": site_name,
            "passed": False,
            "item_count": 0,
            "playback_started": False,
            "message": "Empty directory returned from Kodi",
        }

    # Find first item with a file link
    target_item = None
    for f in files:
        if f.get("file"):
            target_item = f
            break

    if not target_item:
        return {
            "site": site_name,
            "passed": False,
            "item_count": item_count,
            "playback_started": False,
            "message": "No item with playable file link found",
        }

    playback_started = False
    active_item = None
    player_id = 0

    try:
        client.call("Player.Open", {"item": {"file": target_item["file"]}})
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                players = client.call("Player.GetActivePlayers")
                if isinstance(players, list) and len(players) > 0:
                    player_id = players[0].get("playerid", 0)
                    playback_started = True
                    item_res = client.call(
                        "Player.GetItem",
                        {"playerid": player_id, "properties": ["file", "label"]},
                    )
                    if isinstance(item_res, dict):
                        active_item = item_res.get("item")
                    break
            except Exception:
                pass
            time.sleep(0.5)
    except Exception as exc:
        message = f"Player error: {type(exc).__name__}"
    finally:
        try:
            client.call("Player.Stop", {"playerid": player_id})
        except Exception:
            pass

    passed = playback_started and item_count > 0
    message = "Kodi runtime probe succeeded" if passed else "Kodi playback failed to start"

    return {
        "site": site_name,
        "passed": passed,
        "item_count": item_count,
        "playback_started": playback_started,
        "active_item": active_item,
        "message": message,
    }


def main():
    parser = argparse.ArgumentParser(description="Probe site in running Kodi instance.")
    parser.add_argument("--site", required=True, help="Site name")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--kodi-url", default="http://127.0.0.1:8080/jsonrpc", help="Kodi JSON-RPC URL")
    parser.add_argument("--timeout", type=float, default=15.0, help="Probe timeout in seconds")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = KodiClient(url=args.kodi_url, timeout=args.timeout)
    result = probe_site(client, args.site, timeout=args.timeout)

    json_path = out_dir / f"kodi_probe_{args.site}.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
