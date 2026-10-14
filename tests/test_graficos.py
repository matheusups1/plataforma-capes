import importlib.util
import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parents[1] / "site"


@pytest.fixture(scope="module")
def g():
    sys.path.insert(0, str(SITE))
    spec = importlib.util.spec_from_file_location("graficos", SITE / "graficos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    yield mod
    sys.path.remove(str(SITE))


def test_ticks_redondos(g):
    assert g.ticks(0, 47.7) == [0, 10, 20, 30, 40, 50]
    assert g.ticks(0, 3465) == [0, 1000, 2000, 3000, 4000]


def test_linhas_tem_legenda_rotulo_direto_e_tooltip(g):
    svg = g.linhas(
        [("Sul", [(2013, 30.0), (2024, 41.2)]), ("Norte", [(2013, 10.0), (2024, 19.0)])],
        unidade="percentual",
    )
    assert svg.count('class="viz-serie"') == 2
    assert "<title>Sul · 2024: 41,2%</title>" in svg
    assert 'class="viz-rotulo-fim"' in svg
    assert 'class="viz-legenda"' in svg            # ≥ 2 séries: legenda sempre presente
    assert "var(--viz-s1)" in svg and "var(--viz-s2)" in svg


def test_rotulos_diretos_nao_se_sobrepoem(g):
    svg = g.linhas([("A", [(2013, 50.0), (2024, 50.0)]), ("B", [(2013, 50.2), (2024, 50.2)])], unidade="percentual")
    ys = sorted(float(y) for y in re.findall(r'class="viz-rotulo-fim" x="[\d.]+" y="([\d.]+)"', svg))
    assert ys[1] - ys[0] >= 13


def test_barras_h_proporcionais(g):
    html = g.barras_h([("Biológicas", 58.8), ("Multidisciplinar", 25.7)], unidade="percentual")
    larguras = [float(w) for w in re.findall(r"width:([\d.]+)%", html)]
    assert larguras[0] == 100.0 and round(larguras[1], 1) == round(100 * 25.7 / 58.8, 1)
    assert "58,8%" in html


def test_colunas_empilhadas_somam_100_por_ano(g):
    svg = g.colunas_empilhadas(
        anos=[2013, 2014],
        categorias=[("≤3", "var(--viz-o1)"), ("7", "var(--viz-o5)")],
        valores={"≤3": {2013: 3, 2014: 1}, "7": {2013: 1, 2014: 1}},
    )
    assert svg.count("<rect") == 4
    assert "<title>2013 · ≤3: 3 (75,0%)</title>" in svg


def test_matriz_cores_por_intensidade(g):
    html = g.matriz(["3", "4"], ["3", "4"], [[10, 90], [0, 100]], rotulo_linhas="2020", rotulo_colunas="2021")
    assert "viz-q5" in html and "viz-q0" in html
    assert ">90<" in html


def test_eixo_inteiro_sem_decimais(g):
    assert g._num_eixo(50, "percentual") == "50%"
    assert g._num_eixo(4000, "indice") == "4.000"
    assert g._num_eixo(2.5, "razao") == "2,5"


def test_linhas_eixo_x_livre(g):
    svg = g.linhas([("2024", [(m, 1.0) for m in range(24, 97)])], unidade="percentual",
                   x_marcas=[24, 48, 72, 96], x_sufixo=" meses")
    rotulos_x = [t for t in re.findall(r'text-anchor="middle">([^<]+)<', svg)]
    assert rotulos_x == ["24", "48", "72", "96"]
    assert "<title>2024 · 48 meses: 1,0%</title>" in svg


def test_rotulo_sem_valor(g):
    svg = g.linhas([("2013", [(24, 1.0), (96, 0.1)]), ("2024", [(24, 2.0), (96, 0.1)])], "percentual",
                   valor_no_rotulo=False)
    assert "viz-rotulo-valor" not in svg


def test_margem_direita_acomoda_rotulo_longo(g):
    nome = "Mestrado acadêmico (≤ 24 meses)"
    svg = g.linhas([(nome, [(2013, 40.0), (2024, 36.1)])], "percentual")
    largura = float(re.search(r'viewBox="0 0 ([\d.]+) ', svg).group(1))
    x_rotulo = float(re.search(r'class="viz-rotulo-fim" x="([\d.]+)"', svg).group(1))
    assert largura - x_rotulo >= 0.6 * 12 * len(nome + " 36,1%")


def test_rotulo_de_coluna_quebra_em_duas_linhas(g):
    svg = g.colunas_empilhadas(["Me. acad. 2013", "Dout. 2024"], [("x", "var(--viz-o1)")],
                               {"x": {"Me. acad. 2013": 1, "Dout. 2024": 1}})
    assert "<tspan" in svg and ">Me. acad.<" in svg and ">2013<" in svg


def test_largura_minima_proporcional_ao_viewbox(g):
    svg = g.linhas([("Mestrado acadêmico (≤ 24 meses)", [(2013, 40.0), (2024, 36.1)])], "percentual")
    w = float(re.search(r'viewBox="0 0 ([\d.]+) ', svg).group(1))
    minimo = float(re.search(r"min-width:(\d+)px", svg).group(1))
    assert 12 * minimo / w >= 11
