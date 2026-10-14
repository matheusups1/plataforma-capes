"""Download dos CSVs (camada raw) com retry, checksum e skip quando nada mudou."""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from capes_kb import ckan, manifest
from capes_kb.config import RAW_DIR, Config

log = logging.getLogger(__name__)

TENTATIVAS = 4
TIMEOUT = httpx.Timeout(30.0, read=300.0)


def caminho_raw(dataset: str, r: ckan.Resource) -> Path:
    return RAW_DIR / dataset / str(r.ano) / f"{r.id}.csv"


def _baixar(client: httpx.Client, url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(".part")
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with parcial.open("wb") as f:
                    for chunk in resp.iter_bytes(1 << 20):
                        f.write(chunk)
            parcial.replace(destino)
            return
        except (httpx.HTTPError, OSError) as e:
            if tentativa == TENTATIVAS:
                parcial.unlink(missing_ok=True)
                raise
            espera = 2**tentativa
            log.warning("falha ao baixar %s (%s); nova tentativa em %ss", url, e, espera)
            time.sleep(espera)


def _atualizado(entrada: dict | None, r: ckan.Resource, destino: Path) -> bool:
    return (
        entrada is not None
        and destino.exists()
        and entrada.get("modificado_em") == r.modificado_em
        and entrada.get("sha256") == manifest.sha256(destino)
    )


def ingerir(cfg: Config, nome: str, forcar: bool = False) -> list[dict]:
    ds = cfg.datasets[nome]
    registro = manifest.ler("raw")
    resultados = []
    with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
        recursos = [
            r
            for pkg in ds.packages
            for r in ckan.selecionar_csvs(ckan.package_show(client, cfg.ckan_url, pkg), ds.anos)
        ]
        for r in recursos:
            destino = caminho_raw(nome, r)
            entrada = registro.get(r.id)
            if not forcar and _atualizado(entrada, r, destino):
                log.info("[%s %s] sem mudanças, pulando", nome, r.ano)
                resultados.append({**entrada, "status": "pulado"})
                continue
            log.info("[%s %s] baixando %s", nome, r.ano, r.nome)
            _baixar(client, r.url, destino)
            entrada = {
                "dataset": nome,
                "ano": r.ano,
                "package": r.package,
                "resource": r.nome,
                "url": r.url,
                "path": destino.relative_to(RAW_DIR).as_posix(),
                "bytes": destino.stat().st_size,
                "sha256": manifest.sha256(destino),
                "modificado_em": r.modificado_em,
                "baixado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            registro[r.id] = entrada
            manifest.gravar("raw", registro)
            resultados.append({**entrada, "status": "baixado"})

    anos_encontrados = {e["ano"] for e in resultados}
    faltando = sorted(set(range(ds.anos[0], ds.anos[1] + 1)) - anos_encontrados)
    if faltando:
        log.warning("[%s] anos sem arquivo no portal: %s", nome, faltando)
    return resultados
