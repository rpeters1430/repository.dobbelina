from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_TOOL_PATH = ROOT / "scripts" / "site_tool.py"


def load_site_tool():
    spec = importlib.util.spec_from_file_location("site_tool", SITE_TOOL_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_list_prints_recommended_commands(capsys):
    site_tool = load_site_tool()

    assert site_tool.main(["--list"]) == 0

    output = capsys.readouterr().out
    assert "smoke-live" in output
    assert "playwright-inspect" in output
    assert "logos-validate" in output


def test_workflows_prints_common_site_tasks(capsys):
    site_tool = load_site_tool()

    assert site_tool.main(["--workflows"]) == 0

    output = capsys.readouterr().out
    assert "Add or evaluate a new site" in output
    assert "Test an existing site" in output
    assert "Logo maintenance" in output


def test_command_alias_forwards_to_wrapped_script(monkeypatch):
    site_tool = load_site_tool()
    calls = []

    def fake_call(cmd, cwd):
        calls.append((cmd, cwd))
        return 0

    monkeypatch.setattr(site_tool.subprocess, "call", fake_call)

    assert site_tool.main(["smoke", "--site", "hornyfap"]) == 0

    assert calls == [
        (
            [
                site_tool.sys.executable,
                str(ROOT / "scripts" / "live_smoke_test.py"),
                "--site",
                "hornyfap",
            ],
            str(ROOT),
        )
    ]
