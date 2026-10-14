"""CLI do pipeline (substitui Makefile para funcionar igual em Windows/Linux).

    uv run capes ingest programas      # raw: baixa CSVs do portal
    uv run capes bronze programas      # bronze: CSV → Parquet
    uv run capes perfil programas      # validação: registros/ano e drift de esquema
    uv run capes all programas         # ingest + bronze + perfil
    uv run capes transform             # dbt deps + build (staging, marts, testes)
    uv run capes transform -- run -s stg_programas   # argumentos repassados ao dbt
    uv run capes export                # marts → data/capes_kb.sqlite (consumido pelo site)
    uv run capes site                  # quarto render → site/_site
    uv run capes site -- preview       # qualquer comando quarto após --
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

from capes_kb import bronze, config, export, indicadores, ingest

TRANSFORM_DIR = config.ROOT / "transform"
SITE_DIR = config.ROOT / "site"


def _dbt(args: list[str]) -> int:
    env = {
        **os.environ,
        "CAPES_BRONZE_DIR": config.BRONZE_DIR.as_posix(),
        "CAPES_DUCKDB_PATH": (config.DATA_DIR / "capes.duckdb").as_posix(),
    }
    dbt = Path(sys.executable).parent / "dbt"
    comando = [str(dbt), *args, "--project-dir", str(TRANSFORM_DIR), "--profiles-dir", str(TRANSFORM_DIR)]
    return subprocess.run(comando, cwd=TRANSFORM_DIR, env=env).returncode


def transformar(args_dbt: list[str]) -> int:
    indicadores.gerar_seed()  # catálogo YAML → seed, para o dbt testar a correspondência
    if not (TRANSFORM_DIR / "dbt_packages").exists():
        if codigo := _dbt(["deps"]):
            return codigo
    return _dbt(args_dbt or ["build"])


def site(args_quarto: list[str]) -> int:
    env = {**os.environ, "QUARTO_PYTHON": sys.executable, "CAPES_KB_SQLITE": export.SQLITE.as_posix()}
    quarto = Path(sys.executable).parent / "quarto"
    return subprocess.run([str(quarto), *(args_quarto or ["render"])], cwd=SITE_DIR, env=env).returncode


def _imprimir_perfil(nome: str) -> None:
    p = bronze.perfil(nome)
    print(f"\n== {nome}: registros por ano")
    for ano, n in p["linhas_por_ano"].items():
        print(f"  {ano}: {n:>10,}".replace(",", "."))
    print(f"  total: {sum(p['linhas_por_ano'].values()):>9,}".replace(",", "."))
    print(f"\n== {nome}: {len(p['colunas_comuns'])} colunas presentes em todos os anos")
    if p["colunas_parciais"]:
        print(f"== {nome}: colunas que só existem em alguns anos (harmonizar no staging)")
        for col, anos in p["colunas_parciais"].items():
            print(f"  {col}: {anos[0]}–{anos[-1]} ({len(anos)} anos)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capes", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("comando", choices=["ingest", "bronze", "perfil", "all", "transform", "export", "site"])
    parser.add_argument("datasets", nargs="*", help="datasets de config/datasets.yml (padrão: todos)")
    parser.add_argument("--forcar", action="store_true", help="refaz mesmo sem mudanças")
    parser.add_argument("--limpar-raw", action="store_true",
                        help="apaga os CSVs de cada dataset após convertê-los (CI: limita o pico de disco)")
    parser.add_argument("-v", "--verbose", action="store_true")
    argv = sys.argv[1:] if argv is None else argv
    args_extra = argv[argv.index("--") + 1 :] if "--" in argv else []
    args = parser.parse_args(argv[: argv.index("--")] if "--" in argv else argv)

    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # console do Windows não é UTF-8 por padrão

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.comando == "transform":
        return transformar(args_extra)
    if args.comando == "site":
        return site(args_extra)
    if args.comando == "export":
        for tabela, n in export.para_sqlite().items():
            logging.info("%s: %s linhas", tabela, f"{n:,}".replace(",", "."))
        logging.info("gerado %s (%.1f MB)", export.SQLITE, export.SQLITE.stat().st_size / 1e6)
        return 0

    cfg = config.carregar()
    nomes = args.datasets or list(cfg.datasets)
    desconhecidos = set(nomes) - set(cfg.datasets)
    if desconhecidos:
        parser.error(f"dataset(s) desconhecido(s): {', '.join(sorted(desconhecidos))}")

    for nome in nomes:
        if args.comando in ("ingest", "all"):
            ingest.ingerir(cfg, nome, forcar=args.forcar)
        if args.comando in ("bronze", "all"):
            bronze.converter(cfg, nome, forcar=args.forcar)
            if args.limpar_raw:
                shutil.rmtree(config.RAW_DIR / nome, ignore_errors=True)
                logging.info("[%s] CSVs removidos (--limpar-raw)", nome)
        if args.comando in ("perfil", "all"):
            _imprimir_perfil(nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
