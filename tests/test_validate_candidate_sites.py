from pathlib import Path

from scripts import validate_candidate_sites


def test_parse_candidates_reads_known_queue_rows(tmp_path: Path):
    report = tmp_path / "rank.md"
    report.write_text(
        "\n".join(
            [
                "## In Roadmap/Tracker but Not Yet Implemented",
                "",
                "| Site | URL | Category | Difficulty | Sources |",
                "| :--- | :--- | :--- | :--- | :--- |",
                "| **TubePornClassic** | https://tubepornclassic.com | Adult Movies / Grindhouse | easy | roadmap |",
            ]
        ),
        encoding="utf-8",
    )

    candidates = validate_candidate_sites.parse_candidates(
        report, {"In Roadmap/Tracker but Not Yet Implemented"}
    )

    assert len(candidates) == 1
    assert candidates[0].name == "TubePornClassic"
    assert candidates[0].difficulty == "easy"


def test_likely_video_links_keeps_same_site_video_paths():
    html = """
    <a href="/categories">Categories</a>
    <a href="/popular">Popular</a>
    <a href="/video/123/example">Watch scene</a>
    <a href="/videos">Videos index</a>
    <a href="https://other.test/video/999">External</a>
    """

    assert validate_candidate_sites.likely_video_links("https://example.test", html) == [
        "https://example.test/video/123/example"
    ]
