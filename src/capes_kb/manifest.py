"""Manifests versionados (data/manifest/*.json): registram o que foi baixado/convertido,
com checksums, para tornar o pipeline idempotente e auditável sem versionar os dados."""

import hashlib
import json
from pathlib import Path

from capes_kb.config import DATA_DIR

MANIFEST_DIR = DATA_DIR / "manifest"


def sha256(path: Path, bloco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(bloco):
            h.update(chunk)
    return h.hexdigest()


def ler(nome: str) -> dict:
    path = MANIFEST_DIR / f"{nome}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def gravar(nome: str, dados: dict) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / f"{nome}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)
