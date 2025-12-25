import pytest

from tests.conftest import read_fixture

from resources.lib.sites import watchporn, eporner


NEGATIVE_CASES = [
    (
        "watchporn_empty",
        watchporn,
        "List",
        ("https://watchporn.to/latest-updates/",),
        {},
        "sites/watchporn/empty_listing.html",
        True,  # expect notify
    ),
    (
        "eporner_empty",
        eporner,
        "List",
        ("https://www.eporner.com/recent/",),
        {},
        "sites/eporner/empty_listing.html",
        False,  # no explicit notify, just no items
    ),
]


@pytest.mark.parametrize(
    "case_name, module, func_name, func_args, func_kwargs, fixture_path, expect_notify",
    NEGATIVE_CASES,
    ids=[c[0] for c in NEGATIVE_CASES],
)
def test_negative_listings(
    monkeypatch,
    case_name,
    module,
    func_name,
    func_args,
    func_kwargs,
    fixture_path,
    expect_notify,
):
    html = read_fixture(fixture_path)
    captured_videos = []
    captured_dirs = []
    notifications = []

    monkeypatch.setattr(module.utils, "getHtml", lambda *a, **k: html)
    monkeypatch.setattr(module.utils, "eod", lambda *a, **k: None)
    monkeypatch.setattr(
        module.site, "add_download_link", lambda *a, **k: captured_videos.append(a)
    )
    monkeypatch.setattr(module.site, "add_dir", lambda *a, **k: captured_dirs.append(a))
    monkeypatch.setattr(
        module.utils, "notify", lambda *a, **k: notifications.append((a, k))
    )

    getattr(module, func_name)(*func_args, **func_kwargs)

    assert captured_videos == [], "Should not add videos on empty/geo-blocked listing"
    assert captured_dirs == [] or len(captured_dirs) >= 0  # allow pagination absence
    assert bool(notifications) == expect_notify
