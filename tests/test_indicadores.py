import csv

import pytest

from capes_kb import indicadores


def _yml(tmp_path, corpo):
    p = tmp_path / "ind.yml"
    p.write_text(corpo, encoding="utf-8")
    return p


BASE = """
modulos:
  m1: Módulo 1
indicadores:
  x_total:
    nome: X
    modulo: m1
    definicao: def
    formula: count(x)
    unidade: contagem
    fontes: [programas]
    modelo_dbt: mart_x
"""


def test_catalogo_real_e_valido():
    cat = indicadores.carregar()
    assert len(cat) >= 20
    assert all(i.modulo in indicadores.carregar_modulos() for i in cat)


def test_rejeita_unidade_invalida(tmp_path):
    with pytest.raises(ValueError, match="unidade"):
        indicadores.carregar(_yml(tmp_path, BASE.replace("contagem", "litros")))


def test_rejeita_modulo_inexistente(tmp_path):
    with pytest.raises(ValueError, match="modulo"):
        indicadores.carregar(_yml(tmp_path, BASE.replace("modulo: m1", "modulo: m9")))


def test_rejeita_campo_faltando(tmp_path):
    with pytest.raises(ValueError, match="formula"):
        indicadores.carregar(_yml(tmp_path, BASE.replace("    formula: count(x)\n", "")))


def test_gera_seed_csv(tmp_path):
    destino = tmp_path / "indicadores.csv"
    indicadores.gerar_seed(_yml(tmp_path, BASE), destino)
    linhas = list(csv.DictReader(destino.open(encoding="utf-8")))
    assert linhas[0]["indicador_id"] == "x_total"
    assert linhas[0]["fontes"] == "programas"
    assert linhas[0]["modulo_nome"] == "Módulo 1"
