from capes_kb import cli, config


def test_limpar_raw_remove_csvs_apos_bronze(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    (raw / "programas" / "2024").mkdir(parents=True)
    (raw / "programas" / "2024" / "x.csv").write_text("a;b\n1;2\n", encoding="utf-8")
    monkeypatch.setattr(config, "RAW_DIR", raw)
    chamadas = []
    monkeypatch.setattr(cli.bronze, "converter", lambda cfg, nome, forcar=False: chamadas.append(nome))

    assert cli.main(["bronze", "programas", "--limpar-raw"]) == 0

    assert chamadas == ["programas"]
    assert not (raw / "programas").exists()
