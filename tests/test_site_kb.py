import importlib.util
import sqlite3
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "site" / "kb.py"


@pytest.fixture
def kb(tmp_path, monkeypatch):
    db = tmp_path / "kb.sqlite"
    con = sqlite3.connect(db)
    con.executescript("""
        create table indicador (indicador_id, nome, modulo, unidade);
        insert into indicador values ('x', 'Programas', 'm1', 'contagem'), ('p', 'Nota 5+', 'm1', 'percentual');
        create table indicador_valor (indicador_id, ano, recorte_tipo, recorte_valor, valor);
        insert into indicador_valor values
          ('x', 2023, 'brasil', 'BRASIL', 4000), ('x', 2024, 'brasil', 'BRASIL', 4635),
          ('p', 2023, 'brasil', 'BRASIL', 30.0), ('p', 2024, 'brasil', 'BRASIL', 38.5);
    """)
    con.commit()
    con.close()
    monkeypatch.setenv("CAPES_KB_SQLITE", str(db))
    spec = importlib.util.spec_from_file_location("kb", SITE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_formatacao_pt_br(kb):
    assert kb.fmt(4635, "contagem") == "4.635"
    assert kb.fmt(38.456, "percentual") == "38,5%"
    assert kb.fmt(54.66, "meses") == "54,7 meses"
    assert kb.fmt(None, "razao") == "—"


def test_delta_percentual_em_pontos_e_contagem_em_pct(kb):
    assert kb.fmt_delta(38.5, 30.0, "percentual") == "▲ +8,5 p.p."
    assert kb.fmt_delta(4635, 4000, "contagem") == "▲ +15,9%"


def test_stat_tile_tem_valor_delta_e_tooltip_por_ano(kb):
    ind = kb.indicadores()[0]
    tile = kb.stat_tile(ind, link="indicadores.html#ind-x")
    assert "4.635" in tile and "▲ +15,9%" in tile
    assert "<title>2023: 4.000</title>" in tile
    assert 'href="indicadores.html#ind-x"' in tile


def test_indice_grande_sem_decimais(kb):
    assert kb.fmt(2183.4, "indice") == "2.183"
    assert kb.fmt(4.43, "indice") == "4,4"
