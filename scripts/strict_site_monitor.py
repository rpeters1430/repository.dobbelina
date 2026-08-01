#!/usr/bin/env python3
"""Strict site monitor for priority sites."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.listing_validator import validate_listing
from scripts.live_smoke_test import get_site_profile, run_site_child
from scripts.media_validator import validate_media
from scripts.site_health_types import HealthState, ValidationResult, failure_signature, redact_url


def evaluate_record(
    record: dict[str, Any],
    profile: dict[str, Any],
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a site execution record against its strict contract."""
    site_name = record.get("site", "unknown")
    contract = profile.get("strict_contract", {})
    required_stages = list(contract.get("required_stages", ["listing", "playback", "media"]))

    harness = profile.get("harness", {})
    supports = profile.get("supports", {})
    if harness.get("playback_not_testable") or not supports.get("play", True):
        required_stages = [s for s in required_stages if s not in ("playback", "media")]

    # Harness / Infrastructure error
    if record.get("status") == "ERROR" or (not record and "error" in record):
        return {
            "site": site_name,
            "state": HealthState.HARNESS_ERROR,
            "exit_code": 2,
            "classification": "HARNESS_ERROR",
            "message": record.get("error", "Infrastructure or harness error"),
            "failure_signature": failure_signature({
                "state": HealthState.HARNESS_ERROR,
                "failed_stage": "harness",
                "classification": "HARNESS_ERROR",
                "message": record.get("error", "Infrastructure or harness error"),
            }),
            "record": record,
        }

    if not record:
        return {
            "site": site_name,
            "state": HealthState.NOT_TESTED,
            "exit_code": 2,
            "classification": "NOT_TESTED",
            "message": "No execution record available",
            "failure_signature": "",
            "record": {},
        }

    listing_samples = record.get("listing_samples", [])
    listing_res: ValidationResult = validate_listing(listing_samples, contract, baseline)

    steps = record.get("steps", {})
    play_step = steps.get("play", {})
    play_url = play_step.get("play_url") or play_step.get("sample_url", "")

    media_res: ValidationResult | None = None
    if "media_result" in record:
        mr = record["media_result"]
        if isinstance(mr, ValidationResult):
            media_res = mr
        elif isinstance(mr, dict):
            media_res = ValidationResult(
                passed=mr.get("passed", False),
                classification=mr.get("classification", "UNKNOWN"),
                message=mr.get("message", ""),
                metrics=mr.get("metrics", {}),
                evidence=mr.get("evidence", {}),
            )
    elif play_url and "media" in required_stages:
        allowed_hosts = contract.get("allowed_hosts", [])
        media_res = validate_media(play_url, allowed_hosts)

    # Determine state based on evaluation
    failed_stage = None
    classification = "NONE"
    message = "All strict checks passed"
    is_blocked = False

    if not listing_res.passed:
        failed_stage = "listing"
        classification = listing_res.classification
        message = f"Listing failed: {listing_res.message}"
        if classification in ("CHALLENGE", "BLOCKED"):
            is_blocked = True

    if not is_blocked and failed_stage is None and media_res and not media_res.passed:
        failed_stage = "media"
        classification = media_res.classification
        message = f"Media probing failed: {media_res.message}"
        if classification in ("CHALLENGE", "HTML_PAYLOAD", "BLOCKED"):
            is_blocked = True

    if not is_blocked and failed_stage is None:
        for stage in required_stages:
            if stage == "listing" and not listing_res.passed:
                failed_stage = "listing"
                break
            elif stage == "playback":
                p_status = play_step.get("status", "SKIP")
                if p_status not in ("PASS", "HEALTHY"):
                    failed_stage = "playback"
                    classification = "PLAYBACK_FAILED"
                    message = f"Playback step failed or skipped ({p_status})"
                    break
            elif stage == "media" and media_res and not media_res.passed:
                failed_stage = "media"
                break

    if is_blocked:
        state = HealthState.BLOCKED
        exit_code = 1
    elif failed_stage:
        state = HealthState.BROKEN
        exit_code = 1
    else:
        state = HealthState.HEALTHY
        exit_code = 0

    sig = ""
    if state != HealthState.HEALTHY:
        sig = failure_signature({
            "state": state,
            "failed_stage": failed_stage or "unknown",
            "classification": classification,
            "message": message,
        })

    return {
        "site": site_name,
        "state": state,
        "exit_code": exit_code,
        "failed_stage": failed_stage,
        "classification": classification,
        "message": message,
        "failure_signature": sig,
        "listing_metrics": listing_res.metrics if listing_res else {},
        "media_metrics": media_res.metrics if media_res else {},
        "evidence": {
            "listing": listing_res.evidence if listing_res else {},
            "media": media_res.evidence if media_res else {},
            "play_url": redact_url(play_url),
        },
        "record": record,
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    """Render markdown summary of a strict site evaluation."""
    site = report.get("site", "unknown")
    state = report.get("state", "UNKNOWN")
    msg = report.get("message", "")
    sig = report.get("failure_signature", "")

    lines = [
        f"# Strict Site Health: `{site}`",
        f"- **State:** **`{state}`**",
        f"- **Message:** {msg}",
    ]
    if sig:
        lines.append(f"- **Failure Signature:** `{sig}`")

    listing_m = report.get("listing_metrics", {})
    if listing_m:
        lines.extend([
            "",
            "## Listing Metrics",
            f"- **Item Count:** {listing_m.get('item_count', 0)}",
            f"- **Unique Title Ratio:** {listing_m.get('unique_title_ratio', 0.0)}",
            f"- **Unique URL Ratio:** {listing_m.get('unique_url_ratio', 0.0)}",
        ])

    media_m = report.get("media_metrics", {})
    if media_m:
        lines.extend([
            "",
            "## Media Metrics",
            f"- **Media Kind:** `{media_m.get('media_kind', 'unknown')}`",
            f"- **Segment Bytes:** {media_m.get('segment_bytes', 0)}",
        ])

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Run strict site monitor for a priority site.")
    parser.add_argument("--site", required=True, help="Site name (e.g. pornhub)")
    parser.add_argument("--out", required=True, help="Output directory for reports")
    parser.add_argument("--baseline", help="Path to previous strict result baseline JSON file")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = get_site_profile(args.site)
    baseline_data = None
    if args.baseline and Path(args.baseline).exists():
        try:
            baseline_data = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        except Exception:
            baseline_data = None

    record = run_site_child(args.site, strict=True)
    report = evaluate_record(record, profile, baseline_data)

    json_path = out_dir / f"strict_site_{args.site}.json"
    md_path = out_dir / f"strict_site_{args.site}.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")

    sys.exit(report["exit_code"])


if __name__ == "__main__":
    main()
