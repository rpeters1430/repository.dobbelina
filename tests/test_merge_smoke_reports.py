from pathlib import Path

from scripts.merge_smoke_reports import discover_report_paths


def test_discover_report_paths_supports_flat_and_nested_artifacts(tmp_path: Path):
    flat = tmp_path / "live_smoke_chunk_0.json"
    nested = tmp_path / "artifact" / "live_smoke_chunk_1.json"
    unrelated = tmp_path / "artifact" / "summary.json"
    flat.touch()
    nested.parent.mkdir()
    nested.touch()
    unrelated.touch()

    assert discover_report_paths(tmp_path) == [flat, nested]
