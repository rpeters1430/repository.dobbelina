import importlib
import sys


def _load_default_module():
    sys.modules.pop("default", None)
    return importlib.import_module("default")


def test_main_defaults_to_index_when_query_missing():
    default_module = _load_default_module()

    captured = {}

    def fake_dispatch(mode, queries):
        captured["mode"] = mode
        captured["queries"] = queries

    default_module.url_dispatcher.dispatch = fake_dispatch

    default_module.main(["plugin.video.cumination", "1"])

    assert captured["mode"] == "main.INDEX"
    assert captured["queries"]["mode"] == "main.INDEX"


def test_main_dispatches_explicit_query_mode():
    default_module = _load_default_module()

    captured = {}

    def fake_dispatch(mode, queries):
        captured["mode"] = mode
        captured["queries"] = queries

    default_module.url_dispatcher.dispatch = fake_dispatch

    default_module.main(
        [
            "plugin.video.cumination",
            "1",
            "?mode=main.site_list&url=https%3A%2F%2Fexample.com",
        ]
    )

    assert captured["mode"] == "main.site_list"
    assert captured["queries"]["url"] == "https://example.com"
