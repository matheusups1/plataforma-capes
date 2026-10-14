"""Catálogo de indicadores (indicators/indicadores.yml): validação e seed para o dbt.

O YAML é a fonte única da documentação. O seed gerado permite ao dbt testar que todo
indicador documentado é calculado em mart_indicador_valor, e vice-versa.
"""

import csv
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

from capes_kb.config import ROOT

CATALOGO = ROOT / "indicators" / "indicadores.yml"
SEED = ROOT / "transform" / "seeds" / "indicadores.csv"
UNIDADES = {"contagem", "percentual", "razao", "meses", "indice"}
OBRIGATORIOS = ("nome", "modulo", "definicao", "formula", "unidade", "fontes", "modelo_dbt")


@dataclass(frozen=True)
class Indicador:
    indicador_id: str
    nome: str
    modulo: str
    modulo_nome: str
    definicao: str
    formula: str
    unidade: str
    fontes: str
    modelo_dbt: str
    limitacoes: str = ""
    interpretacao: str = ""


def _ler(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def carregar_modulos(path: Path = CATALOGO) -> dict[str, str]:
    return _ler(path)["modulos"]


def carregar(path: Path = CATALOGO) -> list[Indicador]:
    bruto = _ler(path)
    modulos = bruto["modulos"]
    resultado = []
    for iid, d in bruto["indicadores"].items():
        faltando = [c for c in OBRIGATORIOS if not d.get(c)]
        if faltando:
            raise ValueError(f"{iid}: campos obrigatórios ausentes: {', '.join(faltando)}")
        if d["unidade"] not in UNIDADES:
            raise ValueError(f"{iid}: unidade '{d['unidade']}' inválida (use {sorted(UNIDADES)})")
        if d["modulo"] not in modulos:
            raise ValueError(f"{iid}: modulo '{d['modulo']}' não declarado em `modulos`")
        resultado.append(
            Indicador(
                indicador_id=iid,
                nome=d["nome"],
                modulo=d["modulo"],
                modulo_nome=modulos[d["modulo"]],
                definicao=" ".join(d["definicao"].split()),
                formula=d["formula"],
                unidade=d["unidade"],
                fontes=",".join(d["fontes"]),
                modelo_dbt=d["modelo_dbt"],
                limitacoes=" ".join(d.get("limitacoes", "").split()),
                interpretacao=" ".join(d.get("interpretacao", "").split()),
            )
        )
    return resultado


def gerar_seed(path: Path = CATALOGO, destino: Path = SEED) -> Path:
    catalogo = carregar(path)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(catalogo[0])))
        w.writeheader()
        w.writerows(asdict(i) for i in catalogo)
    return destino
