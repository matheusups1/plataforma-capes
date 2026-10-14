import sqlite3

import duckdb
import pytest

from capes_kb import export


@pytest.fixture
def duck(tmp_path):
    path = tmp_path / "capes.duckdb"
    con = duckdb.connect(str(path))
    con.execute("""
        create table mart_indicador_valor as select * from (values
            ('prog_total', 2024, 'brasil', 'BRASIL', 4635.0, null, null, 'contagem', null),
            ('prog_total', 2024, 'regiao', 'SUL', 900.0, null, null, 'contagem', null)
        ) t(indicador_id, ano, recorte_tipo, recorte_valor, valor, numerador, denominador, unidade, variacao_anual_pct);
        create table dim_area_avaliacao as select 2 as cd_area_avaliacao, 'COMPUTAÇÃO' as nm_area_avaliacao,
            'CIÊNCIAS EXATAS' as grande_area, ['CIÊNCIA DA COMPUTAÇÃO', 'COMPUTAÇÃO'] as nomes_historicos,
            2013 as primeiro_ano, 2024 as ultimo_ano;
        create table dim_ies as select '10001018' as cd_ies, 'UNIR' as sg_ies;
        create table fct_programa_ano as select 2024 as ano, '10001018002P1' as cd_programa, true as em_rede;
    """)
    con.close()
    return path


def test_exporta_tabelas_permitidas(duck, tmp_path):
    destino = tmp_path / "kb.sqlite"
    resumo = export.para_sqlite(duck, destino)

    con = sqlite3.connect(destino)
    tabelas = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    assert {"indicador", "indicador_valor", "modulo", "area_avaliacao", "ies", "programa_ano", "fonte", "metadados"} <= tabelas
    assert con.execute("select count(*) from indicador_valor").fetchone()[0] == 2
    assert con.execute("select nomes_historicos from area_avaliacao").fetchone()[0] == "CIÊNCIA DA COMPUTAÇÃO; COMPUTAÇÃO"
    assert con.execute("select em_rede from programa_ano").fetchone()[0] == 1
    assert con.execute("select count(*) from indicador").fetchone()[0] >= 20
    assert resumo["indicador_valor"] == 2


def test_bloqueia_coluna_pessoal(duck, tmp_path, monkeypatch):
    monkeypatch.setitem(export.TABELAS, "vazamento", "select 'x' as nm_docente")
    with pytest.raises(ValueError, match="nm_docente"):
        export.para_sqlite(duck, tmp_path / "kb.sqlite")
