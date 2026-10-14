import pytest

from capes_kb.ckan import Resource, ano_do_recurso, selecionar_csvs


@pytest.mark.parametrize(
    "nome, esperado",
    [
        ("BR-CAPES-COLSUCUP-PROG-2013A2016-2020-06-12_2013", 2013),
        ("BR-CAPES-COLSUCUP-PROG-2013A2016-2020-06-12_2016", 2016),
        ("BR-CAPES-COLSUCUP-PROG-2017-2021-11-10", 2017),
        ("BR-CAPES-COLSUCUP-DISCENTES-2024-2025-12-01", 2024),
        ("BR-CAPES-COLSUCUP-PROD-AUTOR-2021A2024-2025-12-01-BIBLIOGRAFICA-ARTPE-2022", 2022),
        ("Metadados de Programas da Pós-Graduação", None),
    ],
)
def test_ano_do_recurso(nome, esperado):
    assert ano_do_recurso(nome) == esperado


def _res(nome, fmt="CSV", rid=None):
    return {"id": rid or nome, "name": nome, "format": fmt, "url": f"https://x/{nome}.csv", "size": 10}


def test_selecionar_csvs_filtra_formato_e_anos():
    pacote = {
        "name": "pkg",
        "resources": [
            _res("BR-CAPES-COLSUCUP-PROG-2013A2016-2020-06-12_2013"),
            _res("BR-CAPES-COLSUCUP-PROG-2013A2016-2020-06-12_2013", fmt="XLSX", rid="x"),
            _res("BR-CAPES-COLSUCUP-PROG-2013A2016-2020-06-12_2016"),
            _res("Metadados", fmt="PDF"),
        ],
    }
    sel = selecionar_csvs(pacote, anos=(2014, 2024))
    assert [r.ano for r in sel] == [2016]
    assert isinstance(sel[0], Resource)
    assert sel[0].package == "pkg"
