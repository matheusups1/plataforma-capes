"""CLI do pipeline (substitui Makefile para funcionar igual em Windows/Linux).

    uv run capes ingest programas      # raw: baixa CSVs do portal
    uv run capes bronze programas      # bronze: CSV → Parquet
    uv run capes perfil programas      # validação: registros/ano e drift de esquema
    uv run capes all programas         # ingest + bronze + perfil
"""

import argparse
import logging
import sys

from capes_kb import bronze, config, ingest


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
    parser.add_argument("comando", choices=["ingest", "bronze", "perfil", "all"])
    parser.add_argument("datasets", nargs="*", help="datasets de config/datasets.yml (padrão: todos)")
    parser.add_argument("--forcar", action="store_true", help="refaz mesmo sem mudanças")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # console do Windows não é UTF-8 por padrão

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)

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
        if args.comando in ("perfil", "all"):
            _imprimir_perfil(nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
