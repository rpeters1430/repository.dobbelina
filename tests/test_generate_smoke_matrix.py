import importlib
import json


def test_main_outputs_valid_matrix(monkeypatch, tmp_path, capsys):
    generate_smoke_matrix = importlib.import_module("scripts.generate_smoke_matrix")

    sites_dir = tmp_path / "sites"
    sites_dir.mkdir()
    for site_name in ["alpha", "beta", "gamma", "delta", "epsilon"]:
        (sites_dir / f"{site_name}.py").write_text("", encoding="utf-8")
    (sites_dir / "__init__.py").write_text("", encoding="utf-8")
    (sites_dir / "soup_spec.py").write_text("", encoding="utf-8")

    profiles_path = tmp_path / "site_profiles.json"
    profiles_path.write_text('{"sites":{"alpha":{"tier":1}}}', encoding="utf-8")

    monkeypatch.setattr(generate_smoke_matrix, "SITES_DIR", sites_dir)
    monkeypatch.setattr(generate_smoke_matrix, "SITE_PROFILES_PATH", profiles_path)

    generate_smoke_matrix.main()

    matrix = json.loads(capsys.readouterr().out)

    assert [entry["chunk"] for entry in matrix["include"]] == [1, 2, 3, 4]
    assert sorted(
        site
        for entry in matrix["include"]
        for site in entry["sites"].split()
    ) == ["alpha", "beta", "delta", "epsilon", "gamma"]
