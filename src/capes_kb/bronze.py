"""CSV (raw) → Parquet (bronze).

Bronze é 1:1 com a fonte: todas as colunas como VARCHAR, nomes originais,
mais `_ano` e `_resource_id`. Tipagem e harmonização entre períodos ficam
no staging (dbt), onde podem ser testadas.
"""

import codecs
import logging
from pathlib import Path

import duckdb

from capes_kb import manifest
from capes_kb.config import BRONZE_DIR, RAW_DIR, Config

log = logging.getLogger(__name__)


def _byte_como_latin1(erro: UnicodeDecodeError) -> tuple[str, int]:
    # bytes que o cp1252 não define (0x81, 0x8D, 0x8F, 0x90, 0x9D) caem para latin-1
    return erro.object[erro.start : erro.end].decode("latin-1"), erro.end


codecs.register_error("latin1_fallback", _byte_como_latin1)


def _para_utf8(origem: Path, destino: Path, encoding: str) -> None:
    """Transcodifica em streaming. O portal declara latin-1, mas parte dos arquivos é
    cp1252 (–, ’), que o leitor latin-1 do DuckDB rejeita."""
    decoder = codecs.getincrementaldecoder(encoding)(errors="latin1_fallback")
    with origem.open("rb") as src, destino.open("w", encoding="utf-8", newline="") as dst:
        while chunk := src.read(1 << 20):
            dst.write(decoder.decode(chunk))
        dst.write(decoder.decode(b"", final=True))


def _sql_str(valor: str) -> str:
    return "'" + valor.replace("'", "''") + "'"


def _linhas_fisicas(path: Path) -> int:
    with path.open("rb") as f:
        return sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(1 << 20), b""))


def csv_para_parquet(
    csv: Path, destino: Path, *, ano: int, resource_id: str, delim: str, encoding: str, header: bool = True
) -> dict:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(".tmp.parquet")
    utf8 = destino.with_suffix(".tmp.csv")
    _para_utf8(csv, utf8, encoding)
    leitura = (
        f"read_csv({_sql_str(utf8.as_posix())}, delim={_sql_str(delim)}, encoding='utf-8', "
        f"header={str(header).lower()}, all_varchar=true, quote='\"', null_padding=true, hive_partitioning=false)"
    )
    con = duckdb.connect()
    try:
        con.execute(
            f"COPY (SELECT *, {int(ano)}::INTEGER AS _ano, {_sql_str(resource_id)} AS _resource_id FROM {leitura}) "
            f"TO {_sql_str(tmp.as_posix())} (FORMAT parquet, COMPRESSION zstd)"
        )
        linhas = con.execute(f"SELECT count(*) FROM {_sql_str(tmp.as_posix())}").fetchone()[0]
        colunas = [c[0] for c in con.execute(f"DESCRIBE SELECT * FROM {leitura}").fetchall()]
    finally:
        con.close()
        utf8.unlink(missing_ok=True)
    tmp.replace(destino)
    return {"linhas": linhas, "colunas": colunas}


def converter(cfg: Config, nome: str, forcar: bool = False) -> list[dict]:
    ds = cfg.datasets[nome]
    raw = {rid: e for rid, e in manifest.ler("raw").items() if e["dataset"] == nome}
    registro = manifest.ler("bronze")
    resultados = []
    for rid, e in sorted(raw.items(), key=lambda kv: kv[1]["ano"]):
        origem = RAW_DIR / e["path"]
        destino = BRONZE_DIR / nome / f"ano={e['ano']}" / f"{rid}.parquet"
        anterior = registro.get(rid)
        if not forcar and anterior and anterior.get("origem_sha256") == e["sha256"] and destino.exists():
            resultados.append({**anterior, "status": "pulado"})
            continue
        log.info("[%s %s] convertendo para parquet", nome, e["ano"])
        info = csv_para_parquet(
            origem, destino, ano=e["ano"], resource_id=rid,
            delim=ds.csv["delim"], encoding=ds.csv["encoding"], header=ds.csv.get("header", True),
        )
        fisicas = _linhas_fisicas(origem) - (1 if ds.csv.get("header", True) else 0)
        if fisicas != info["linhas"]:
            # quebras de linha dentro de campos entre aspas geram diferença legítima; registrar para auditoria
            log.warning("[%s %s] linhas físicas=%s ≠ registros=%s", nome, e["ano"], fisicas, info["linhas"])
        entrada = {
            "dataset": nome,
            "ano": e["ano"],
            "path": destino.relative_to(BRONZE_DIR).as_posix(),
            "origem_sha256": e["sha256"],
            "linhas": info["linhas"],
            "linhas_fisicas_csv": fisicas,
            "colunas": info["colunas"],
        }
        registro[rid] = entrada
        manifest.gravar("bronze", registro)
        resultados.append({**entrada, "status": "convertido"})
    return resultados


def perfil(nome: str) -> dict:
    """Resumo para validação: registros por ano e evolução do esquema entre anos."""
    entradas = sorted(
        (e for e in manifest.ler("bronze").values() if e["dataset"] == nome), key=lambda e: e["ano"]
    )
    por_ano: dict[int, dict] = {}
    for e in entradas:
        a = por_ano.setdefault(e["ano"], {"linhas": 0, "colunas": set()})
        a["linhas"] += e["linhas"]
        a["colunas"].update(e["colunas"])
    todas = set().union(*(a["colunas"] for a in por_ano.values())) if por_ano else set()
    comuns = set.intersection(*(a["colunas"] for a in por_ano.values())) if por_ano else set()
    return {
        "linhas_por_ano": {ano: a["linhas"] for ano, a in por_ano.items()},
        "colunas_comuns": sorted(comuns),
        "colunas_parciais": {c: sorted(ano for ano, a in por_ano.items() if c in a["colunas"]) for c in sorted(todas - comuns)},
    }
