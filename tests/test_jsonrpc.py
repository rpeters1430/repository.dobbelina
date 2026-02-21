import json



def test_rpc_request_and_validate_response(monkeypatch):
    from resources.lib import jsonrpc as jsonrpc_module

    logged = []

    def fake_execute(payload):
        request = json.loads(payload)
        assert request["method"] == "Test.Method"
        return json.dumps({"result": {"ok": True}})

    monkeypatch.setattr(
        jsonrpc_module.xbmc, "executeJSONRPC", fake_execute, raising=False
    )
    monkeypatch.setattr(
        jsonrpc_module.xbmc, "log", lambda msg, level=None: logged.append(msg)
    )

    response = jsonrpc_module.rpc_request(
        {"jsonrpc": "2.0", "id": 1, "method": "Test.Method"}
    )
    assert response["result"]["ok"] is True
    assert jsonrpc_module.validate_rpc_response(response, required_attrib=None) is True

    bad_response = {"result": {}}
    assert (
        jsonrpc_module.validate_rpc_response(
            bad_response, request="Missing", required_attrib="settings"
        )
        is False
    )
    assert logged


def test_jsonrpc_payload_building(monkeypatch):
    from resources.lib import jsonrpc as jsonrpc_module

    captured = []

    def fake_rpc_request(payload):
        captured.append(payload)
        return {"ok": True}

    monkeypatch.setattr(jsonrpc_module, "rpc_request", fake_rpc_request)

    jsonrpc_module.jsonrpc({"method": "A"}, {"method": "B", "id": 99})
    assert captured[0][0]["id"] == 0
    assert captured[0][0]["jsonrpc"] == "2.0"
    assert captured[0][1]["id"] == 99

    captured.clear()
    jsonrpc_module.jsonrpc(method="Single")
    assert captured[0]["id"] == 0
    assert captured[0]["jsonrpc"] == "2.0"

    assert jsonrpc_module.jsonrpc({"method": "A"}, method="B") is None


def test_toggle_debug_calls_setting_update(monkeypatch):
    from resources.lib import jsonrpc as jsonrpc_module

    called = {}

    def fake_get_settings():
        return {"result": {"settings": [{"id": "debug.showloginfo", "value": False}]}}

    def fake_debug_show_log_info(value):
        called["value"] = value
        return {"result": {"ok": True}}

    monkeypatch.setattr(jsonrpc_module, "get_settings", fake_get_settings)
    monkeypatch.setattr(jsonrpc_module, "debug_show_log_info", fake_debug_show_log_info)

    assert jsonrpc_module.toggle_debug() is True
    assert called["value"] is True


def test_addon_checks(monkeypatch):
    from resources.lib import jsonrpc as jsonrpc_module

    monkeypatch.setattr(
        jsonrpc_module,
        "jsonrpc",
        lambda **kwargs: {"error": {"message": "missing"}},
    )
    assert jsonrpc_module.has_addon("plugin.demo") is False

    monkeypatch.setattr(jsonrpc_module, "jsonrpc", lambda **kwargs: {"result": {}})
    assert jsonrpc_module.has_addon("plugin.demo") is True

    monkeypatch.setattr(
        jsonrpc_module,
        "jsonrpc",
        lambda **kwargs: {"result": {"addon": {"enabled": True}}},
    )
    assert jsonrpc_module.addon_enabled("plugin.demo") is True

    monkeypatch.setattr(
        jsonrpc_module, "jsonrpc", lambda **kwargs: {"result": {"addon": {}}}
    )
    assert jsonrpc_module.addon_enabled("plugin.demo") is False

    monkeypatch.setattr(jsonrpc_module, "jsonrpc", lambda **kwargs: {"error": "fail"})
    assert jsonrpc_module.enable_addon("plugin.demo") is False

    monkeypatch.setattr(jsonrpc_module, "jsonrpc", lambda **kwargs: {"result": {}})
    assert jsonrpc_module.enable_addon("plugin.demo") is True


def test_install_and_check_addon(monkeypatch):
    from resources.lib import jsonrpc as jsonrpc_module

    import xbmc
    import xbmcaddon

    monkeypatch.setattr(xbmc, "executebuiltin", lambda *a, **k: None)
    monkeypatch.setattr(xbmcaddon, "Addon", lambda *a, **k: object())
    assert jsonrpc_module.install_addon("plugin.demo") is True

    def _raise(*args, **kwargs):
        raise RuntimeError("missing")

    monkeypatch.setattr(xbmcaddon, "Addon", _raise)
    assert jsonrpc_module.install_addon("plugin.demo") is False

    monkeypatch.setattr(jsonrpc_module, "has_addon", lambda *_: False)
    monkeypatch.setattr(jsonrpc_module.dialog, "yesno", lambda *a, **k: False)
    assert jsonrpc_module.check_addon("plugin.demo") is False

    installed = {"called": False}

    def _install(_addonid):
        installed["called"] = True
        return True

    monkeypatch.setattr(jsonrpc_module, "install_addon", _install)
    monkeypatch.setattr(jsonrpc_module.dialog, "yesno", lambda *a, **k: True)
    assert jsonrpc_module.check_addon("plugin.demo") is True
    assert installed["called"] is True

    monkeypatch.setattr(jsonrpc_module, "has_addon", lambda *_: True)
    monkeypatch.setattr(jsonrpc_module, "addon_enabled", lambda *_: False)
    enabled = {"called": False}

    def _enable(_addonid):
        enabled["called"] = True
        return True

    monkeypatch.setattr(jsonrpc_module, "enable_addon", _enable)
    assert jsonrpc_module.check_addon("plugin.demo") is True
    assert enabled["called"] is True
