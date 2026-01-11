import time


def test_setpin_updates_settings(monkeypatch):
    from resources.lib import pin

    settings = {}

    monkeypatch.setattr(pin.xbmcgui, "ALPHANUM_HIDE_INPUT", 0, raising=False)
    monkeypatch.setattr(pin.dialog, "select", lambda *a, **k: 0, raising=False)
    monkeypatch.setattr(pin.dialog, "input", lambda *a, **k: "1234", raising=False)
    monkeypatch.setattr(pin.addon, "setSetting", lambda key, value: settings.update({key: value}))

    pin.SetPin()
    assert settings["pincode"]
    assert settings["logintime"] == ""


def test_setpin_remove_pin(monkeypatch):
    from resources.lib import pin

    settings = {}

    monkeypatch.setattr(pin.dialog, "select", lambda *a, **k: 1, raising=False)
    monkeypatch.setattr(pin.addon, "setSetting", lambda key, value: settings.update({key: value}))

    pin.SetPin()
    assert settings["pincode"] == ""
    assert settings["logintime"] == ""


def test_checkpin_recent_login(monkeypatch):
    from resources.lib import pin

    now = 1000.0
    monkeypatch.setattr(time, "time", lambda: now)
    monkeypatch.setattr(pin.addon, "getSetting", lambda key: str(now))

    assert pin.CheckPin() is True


def test_checkpin_matches_hash(monkeypatch):
    from resources.lib import pin

    now = 5000.0
    expected = pin.HashPin("9999")

    settings = {"pincode": expected, "logintime": "0"}
    monkeypatch.setattr(time, "time", lambda: now)
    monkeypatch.setattr(pin.addon, "getSetting", lambda key: settings.get(key, ""))
    monkeypatch.setattr(pin.addon, "setSetting", lambda key, value: settings.update({key: value}))
    monkeypatch.setattr(pin, "AskPin", lambda: expected)

    assert pin.CheckPin() is True
    assert settings["logintime"] == str(now)


def test_checkpin_rejects_and_no_retry(monkeypatch):
    from resources.lib import pin

    settings = {"pincode": pin.HashPin("2222"), "logintime": "0"}
    monkeypatch.setattr(pin.addon, "getSetting", lambda key: settings.get(key, ""))
    monkeypatch.setattr(pin, "AskPin", lambda: pin.HashPin("1111"))
    monkeypatch.setattr(pin.dialog, "yesno", lambda *a, **k: False, raising=False)

    assert pin.CheckPin() is False
