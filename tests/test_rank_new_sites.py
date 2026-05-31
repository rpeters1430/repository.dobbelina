from pathlib import Path

from scripts import rank_new_sites


def test_parse_tracker_reads_difficulty_column(tmp_path: Path):
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        "\n".join(
            [
                "## Candidate Queue",
                "",
                "| Site | Category | Difficulty | Status | Notes |",
                "|---|---|---:|---|---|",
                "| `pornmd` | Streaming / Search | Easy-Medium | Not started | Search site |",
                "| `javdoe` | JAV | Hard | Not started | Host chain |",
            ]
        ),
        encoding="utf-8",
    )

    assert rank_new_sites.parse_tracker(tracker) == {
        "pornmd": "easy-medium",
        "javdoe": "hard",
    }


def test_parse_new_sites_marks_integrated_table_rows_implemented(tmp_path: Path):
    new_sites = tmp_path / "NEW_SITES.md"
    new_sites.write_text(
        "\n".join(
            [
                "## Tier 1 - Easy",
                "| Site | Category | Difficulty | Status | Notes |",
                "| :--- | :--- | :--- | :--- | :--- |",
                "| **PornoBae** | Tube | Easy | ✅ | **Integrated** |",
                "| **PornMD** | Aggregator | Medium | [ ] | Active |",
                "| **TopVid** | Changed | Now a video ad maker service |",
            ]
        ),
        encoding="utf-8",
    )

    parsed = rank_new_sites.parse_new_sites(new_sites)

    assert parsed["pornobae"] == "implemented"
    assert parsed["pornmd"] == "easy"
    assert parsed["topvid"] == "unavailable"


def test_rank_candidates_uses_aliases_and_filters_non_addon_links():
    fluffle_sites = [
        {
            "raw_name": "pornxtheatre",
            "name": "pornxtheatre",
            "url": "https://pornxtheatre.com",
            "category": "Adult Movies / Grindhouse",
        },
        {
            "raw_name": "GitHub",
            "name": "github",
            "url": "https://github.com/example/tool",
            "category": "Tools",
        },
        {
            "raw_name": "PornMD",
            "name": "pornmd",
            "url": "https://www.pornmd.com",
            "category": "Streaming",
        },
        {
            "raw_name": "TopVid",
            "name": "topvid",
            "url": "https://topvid.tv",
            "category": "Streaming",
        },
    ]

    candidates, implemented = rank_new_sites.rank_candidates(
        fluffle_sites,
        existing_modules={"xtheatre"},
        roadmap={},
        tracker={"pornmd": "easy-medium"},
        new_sites_md={"topvid": "unavailable"},
        tracker_implemented={"pornxtheatre"},
    )

    assert [site["raw_name"] for site in implemented] == ["pornxtheatre"]
    assert [site["raw_name"] for site in candidates] == ["PornMD"]
    assert candidates[0]["difficulty"] == "easy-medium"


def test_parse_tracker_implemented_ignores_special_state_section(tmp_path: Path):
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        "\n".join(
            [
                "## Already Supported",
                "- `xtheatre` / `pornxtheatre`",
                "## Existing But Special State",
                "| `pornxpert` | Present but excluded |",
                "## Candidate Queue",
            ]
        ),
        encoding="utf-8",
    )

    assert rank_new_sites.parse_tracker_implemented(tracker) == {
        "xtheatre",
        "pornxtheatre",
    }


def test_site_keys_extracts_real_domain_from_www_and_subdomains():
    site = {
        "raw_name": "JAVMost",
        "name": "javmost",
        "url": "https://www5.javmost.com",
        "category": "Asian / JAV",
    }

    assert "javmost" in rank_new_sites.site_keys(site)
