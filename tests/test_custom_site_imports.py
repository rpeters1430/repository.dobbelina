import sys
import types


def _load_default_module():
    import importlib.util
    import sys
    from pathlib import Path
    
    # Use the absolute path to default.py to ensure we load the correct one
    plugin_path = Path(__file__).resolve().parents[1] / "plugin.video.cumination" / "default.py"
    spec = importlib.util.spec_from_file_location("plugin_default", str(plugin_path))
    mod = importlib.util.module_from_spec(spec)
    # We don't want to register it in sys.modules yet, or maybe we do?
    # Let's just execute it.
    spec.loader.exec_module(mod)
    return mod


def test_custom_site_import_failure_reports(monkeypatch):
    monkeypatch.setitem(sys.modules, "requests", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "resources.lib.sites", types.ModuleType("resources.lib.sites"))
    monkeypatch.setitem(
        sys.modules,
        "websocket",
        types.SimpleNamespace(
            WebSocket=lambda: types.SimpleNamespace(
                send=lambda *a, **k: None, recv=lambda: ""
            ),
            create_connection=lambda *a, **k: types.SimpleNamespace(
                send=lambda *a, **k: None, recv=lambda: ""
            ),
        ),
    )
    
    plugin_default = _load_default_module()
    plugin_default.addon.setSetting("custom_sites", "true")

    disabled_modules = []
    logged_messages = []
    textboxes = []

    fake_favorites = types.SimpleNamespace(
        enabled_custom_sites=lambda: ["custom.bad", "custom.good"],
        disable_custom_site_by_module=lambda module: disabled_modules.append(module),
        get_custom_site_title_by_module=lambda module: "Title {0}".format(module),
    )

    class _Dialog:
        def ok(self, *args, **kwargs):
            pass

        def yesno(self, *args, **kwargs):
            return True

    def fake_import_custom_site(module_name, safe_base):
        if module_name == "custom.bad":
            error = ModuleNotFoundError("No module named 'missing_dependency'")
            error.name = "missing_dependency"
            raise error

    monkeypatch.setattr(plugin_default, "favorites", fake_favorites)
    monkeypatch.setattr(plugin_default, "dialog", _Dialog())
    monkeypatch.setattr(plugin_default, "_import_custom_site", fake_import_custom_site)
    monkeypatch.setattr(
        plugin_default.utils,
        "kodilog",
        lambda message, level=None: logged_messages.append(message),
    )
    monkeypatch.setattr(
        plugin_default.utils,
        "textBox",
        lambda heading, body: textboxes.append((heading, body)),
    )

    results = plugin_default.load_custom_sites()

    assert [entry["module"] for entry in results["loaded"]] == ["custom.good"]
    assert disabled_modules == ["custom.bad"]
    assert any("missing_dependency" in body for _, body in textboxes)
    assert any("custom.bad" in log for log in logged_messages)


def test_custom_sites_health_display(monkeypatch):
    plugin_default = _load_default_module()

    enabled_sites = [
        "custom.good",
        "custom.other",
        "custom.bad",
        "custom.dep",
        "custom.untried",
    ]
    plugin_default.custom_site_import_results["loaded"] = [
        {"module": "custom.other"},
        {"module": "custom.good"},
    ]
    plugin_default.custom_site_import_results["failed"] = [
        {"module": "custom.dep", "dependency": None, "title": None},
        {
            "module": "custom.bad",
            "dependency": "missing_dependency",
            "title": "Title custom.bad",
        },
    ]

    textboxes = []

    fake_favorites = types.SimpleNamespace(
        enabled_custom_sites=lambda: enabled_sites,
        get_custom_site_title_by_module=lambda module: "Title {0}".format(module),
    )

    monkeypatch.setattr(plugin_default, "favorites", fake_favorites)
    monkeypatch.setattr(
        plugin_default.utils,
        "textBox",
        lambda heading, body: textboxes.append((heading, body)),
    )

    plugin_default.custom_sites_health()

    assert textboxes
    heading, body = textboxes[0]
    assert heading == "Custom site health"
    assert body.split("[CR]") == [
        "[B]Loaded custom sites[/B]",
        "• Title custom.good",
        "• Title custom.other",
        "[B]Failed to load[/B]",
        "• Title custom.bad (missing_dependency)",
        "• Title custom.dep (import error)",
        "[B]Not attempted[/B]",
        "• Title custom.untried",
    ]


def test_safe_child_path_rejects_traversal(tmp_path):
    plugin_default = _load_default_module()

    base = tmp_path / "about"
    base.mkdir()

    safe = plugin_default._safe_child_path(str(base), "site.txt")
    assert safe.endswith("site.txt")

    try:
        plugin_default._safe_child_path(str(base), "..\\outside.txt")
    except ValueError:
        pass
    else:
        raise AssertionError("path traversal was accepted")
