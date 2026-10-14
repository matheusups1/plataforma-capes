import duckdb

from capes_kb.bronze import csv_para_parquet


def test_csv_cp1252_vira_parquet_varchar_com_metadados(tmp_path):
    csv = tmp_path / "prog_2013.csv"
    csv.write_bytes(
        "AN_BASE;NM_ENTIDADE_ENSINO;CD_CONCEITO_PROGRAMA\n"
        "2013;UNIVERSIDADE FEDERAL DE RONDÔNIA;3\n"
        '2013;"PONTIFÍCIA; UNIVERSIDADE";A\n'
        "2013;INSTITUTO VALE – DESENVOLVIMENTO;4\n".encode("cp1252")
        + "2013;CASO\x8dINDEFINIDO;5\n".encode("latin-1")  # 0x8D não existe no cp1252
    )
    out = tmp_path / "bronze" / "ano=2013" / "r1.parquet"

    info = csv_para_parquet(csv, out, ano=2013, resource_id="r1", delim=";", encoding="cp1252")

    assert info["linhas"] == 4
    nomes = {r[0] for r in duckdb.sql(f"select NM_ENTIDADE_ENSINO from '{out.as_posix()}'").fetchall()}
    assert "INSTITUTO VALE – DESENVOLVIMENTO" in nomes
    assert "CASO\x8dINDEFINIDO" in nomes
    assert info["colunas"] == ["AN_BASE", "NM_ENTIDADE_ENSINO", "CD_CONCEITO_PROGRAMA"]
    assert "PONTIFÍCIA; UNIVERSIDADE" in nomes
    assert "UNIVERSIDADE FEDERAL DE RONDÔNIA" in nomes
    assert not list(out.parent.glob("*.tmp*")), "arquivos temporários devem ser removidos"
    tipos = dict(duckdb.sql(f"describe select * from '{out.as_posix()}'").fetchall()[i][:2] for i in range(5))
    assert tipos["CD_CONCEITO_PROGRAMA"] == "VARCHAR"
    assert tipos["_ano"] == "INTEGER"
    assert tipos["_resource_id"] == "VARCHAR"
