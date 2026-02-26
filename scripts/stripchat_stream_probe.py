#!/usr/bin/env python3
"""Probe Stripchat stream candidates and report playable/ad/unresolved status."""

import argparse
import json
from urllib.parse import urljoin

import requests

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)


def get_model(username):
    url = "https://stripchat.com/api/external/v4/widget/?limit=1&modelsList={}".format(
        username
    )
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://stripchat.com/{}".format(username),
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    models = data.get("models") or []
    if not models:
        raise RuntimeError("No model returned")
    model = models[0]
    if model.get("username", "").lower() != username.lower():
        raise RuntimeError(
            "API returned different model: {}".format(model.get("username", "unknown"))
        )
    return model


def add_candidates(model):
    out = []
    stream = model.get("stream") or {}
    direct = stream.get("url")
    if isinstance(direct, str) and direct.startswith("http"):
        out.append(("direct", direct))
    urls = stream.get("urls")
    if isinstance(urls, dict):
        for label, u in urls.items():
            if isinstance(u, str) and u.startswith("http"):
                out.append((str(label), u))
    seen = set()
    unique = []
    for label, u in out:
        if u in seen:
            continue
        seen.add(u)
        unique.append((label, u))
    mirrored = []
    for label, u in unique:
        if "edge-hls.saawsedge.com" in u:
            mirrored.append((label + "-mirror", u.replace("edge-hls.saawsedge.com", "edge-hls.doppiocdn.com")))
    return unique + mirrored


def fetch(url):
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": UA})
        return r.status_code, r.text
    except Exception as exc:
        return None, str(exc)


def is_ad_manifest(text):
    if not isinstance(text, str):
        return False
    lower = text.lower()
    return "#ext-x-mouflon-advert" in lower or "/cpa/v2/" in lower


def first_child(master_url, master_text):
    if not isinstance(master_text, str):
        return None
    for line in master_text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return urljoin(master_url, line)
    return None


def probe_candidate(label, url):
    status, body = fetch(url)
    result = {"label": label, "url": url, "master_status": status}
    if status is None:
        result["error"] = body
        result["playable"] = False
        return result
    if status != 200 or "#EXTM3U" not in body:
        result["error"] = "invalid master"
        result["playable"] = False
        return result
    child = first_child(url, body)
    result["master_ad"] = is_ad_manifest(body)
    result["child_url"] = child
    if not child:
        result["playable"] = not result["master_ad"]
        return result
    c_status, c_body = fetch(child)
    result["child_status"] = c_status
    if c_status is None:
        result["child_error"] = c_body
        result["playable"] = False
        return result
    result["child_ad"] = is_ad_manifest(c_body)
    result["playable"] = c_status == 200 and (not result["master_ad"]) and (not result["child_ad"])
    return result


def main():
    parser = argparse.ArgumentParser(description="Probe Stripchat stream URLs for one model")
    parser.add_argument("username", help="Stripchat model username")
    args = parser.parse_args()

    model = get_model(args.username)
    candidates = add_candidates(model)
    results = [probe_candidate(label, url) for label, url in candidates]
    print(json.dumps({"username": args.username, "results": results}, indent=2))


if __name__ == "__main__":
    main()
