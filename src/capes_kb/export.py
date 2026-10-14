"""Gold (DuckDB) → data/capes_kb.sqlite: o único artefato que o site e terceiros consomem.

Só entram as tabelas listadas em TABELAS (agregados e dimensões); microdados de
pessoas nunca saem do DuckDB. Uma checagem de nomes de coluna barra vazamentos.
"""

import re
import sqlite3
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from capes_kb import indicadores, manifest
from capes_kb.config import DATA_DIR

DUCKDB = DATA_DIR / "capes.duckdb"
SQLITE = DATA_DIR / "capes_kb.sqlite"

TABELAS = {
    "indicador_valor": "select * from mart_indicador_valor order by indicador_id, recorte_tipo, recorte_valor, ano",
    "area_avaliacao": """select * replace (array_to_string(nomes_historicos, '; ') as nomes_historicos)
                         from dim_area_avaliacao order by cd_area_avaliacao""",
    "ies": "select * from dim_ies order by cd_ies",
    "programa_ano": "select * from fct_programa_ano order by cd_programa, ano",
    "discentes_programa_ano": "select * from fct_discentes_programa_ano order by cd_programa, nivel, ano",
    "titulacao_meses": "select * from mart_titulacao_meses order by ano, nivel, grande_area, meses",
    "discentes_idade": "select * from mart_discentes_idade order by ano, nivel, evento, faixa_idade",
    "docentes_idade": "select * from mart_docentes_idade order by ano, permanente, faixa_idade",
    "docentes_formacao": "select * from mart_docentes_formacao order by ano, pais_titulacao, sg_ies_titulacao",
    "orientacoes_por_orientador": "select * from mart_orientacoes_por_orientador order by ano, defesas_orientadas",
}

INDICES = {
    "indicador_valor": ["indicador_id, recorte_tipo, ano"],
    "programa_ano": ["ano", "cd_programa"],
    "discentes_programa_ano": ["cd_programa, ano"],
}

_PESSOAL = re.compile(r"^(id_pessoa|nm_(docente|discente|orientador)|nr_documento|cpf|titulo)", re.IGNORECASE)


def _tipo_sqlite(tipo_duckdb: str) -> str:
    t = tipo_duckdb.upper()
    if t in {"BOOLEAN", "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT"}:
        return "INTEGER"
    if t in {"DOUBLE", "FLOAT", "REAL"} or t.startswith("DECIMAL"):
        return "REAL"
    return "TEXT"


def _criar(sq: sqlite3.Connection, nome: str, colunas: list[str], tipos: list[str], linhas: list[tuple]) -> None:
    vazamento = [c for c in colunas if _PESSOAL.match(c)]
    if vazamento:
        raise ValueError(f"tabela {nome}: coluna(s) com dado pessoal não podem ser exportadas: {vazamento}")
    defs = ", ".join(f'"{c}" {t}' for c, t in zip(colunas, tipos))
    sq.execute(f'create table "{nome}" ({defs})')
    marcadores = ", ".join("?" * len(colunas))
    sq.executemany(f'insert into "{nome}" values ({marcadores})', linhas)


def _fontes() -> tuple[list[str], list[tuple]]:
    bronze = manifest.ler("bronze")
    colunas = ["dataset", "ano", "package", "resource", "url", "sha256", "modificado_em", "linhas"]
    linhas = sorted(
        (e["dataset"], e["ano"], e["package"], e["resource"], e["url"], e["sha256"], e["modificado_em"],
         bronze.get(rid, {}).get("linhas"))
        for rid, e in manifest.ler("raw").items()
    )
    return colunas, linhas


def para_sqlite(origem: Path = DUCKDB, destino: Path = SQLITE) -> dict[str, int]:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    resumo = {}
    duck = duckdb.connect(str(origem), read_only=True)
    sq = sqlite3.connect(tmp)
    try:
        for nome, consulta in TABELAS.items():
            rel = duck.sql(consulta)
            linhas = [tuple(float(v) if isinstance(v, Decimal) else v for v in r) for r in rel.fetchall()]
            _criar(sq, nome, rel.columns, [_tipo_sqlite(str(t)) for t in rel.types], linhas)
            resumo[nome] = len(linhas)

        catalogo = indicadores.carregar()
        cols = list(vars(catalogo[0]))
        _criar(sq, "indicador", cols, ["TEXT"] * len(cols), [tuple(vars(i).values()) for i in catalogo])
        modulos = indicadores.carregar_modulos()
        _criar(sq, "modulo", ["modulo", "nome"], ["TEXT", "TEXT"], sorted(modulos.items()))

        cols, linhas = _fontes()
        _criar(sq, "fonte", cols, ["TEXT", "INTEGER", "TEXT", "TEXT", "TEXT", "TEXT", "TEXT", "INTEGER"], linhas)
        _criar(sq, "metadados", ["chave", "valor"], ["TEXT", "TEXT"], [
            ("gerado_em", datetime.now(timezone.utc).isoformat(timespec="seconds")),
            ("fonte_dados", "https://dadosabertos.capes.gov.br"),
        ])

        for tabela, indices in INDICES.items():
            for i, cols_idx in enumerate(indices):
                sq.execute(f'create index "ix_{tabela}_{i}" on "{tabela}" ({cols_idx})')
        sq.commit()
    finally:
        sq.close()
        duck.close()
    tmp.replace(destino)
    return resumo
