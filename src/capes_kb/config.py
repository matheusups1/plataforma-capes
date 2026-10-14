from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "datasets.yml"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"


@dataclass(frozen=True)
class Dataset:
    nome: str
    descricao: str
    modulo: str
    anos: tuple[int, int]
    packages: list[str]
    csv: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Config:
    ckan_url: str
    datasets: dict[str, Dataset]


def carregar(path: Path = CONFIG_PATH) -> Config:
    bruto = yaml.safe_load(path.read_text(encoding="utf-8"))
    defaults = bruto.get("defaults", {})
    datasets = {}
    for nome, d in bruto["datasets"].items():
        datasets[nome] = Dataset(
            nome=nome,
            descricao=d.get("descricao", ""),
            modulo=d.get("modulo", ""),
            anos=tuple(d["anos"]),
            packages=list(d["packages"]),
            csv={**defaults.get("csv", {}), **d.get("csv", {})},
        )
    return Config(ckan_url=defaults["ckan_url"].rstrip("/"), datasets=datasets)
