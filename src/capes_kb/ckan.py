"""Cliente mínimo da API CKAN do portal de dados abertos da CAPES.

As URLs dos arquivos mudam a cada republicação, então nunca são fixadas:
são resolvidas a cada execução via `package_show`.
"""

import re
from dataclasses import dataclass

import httpx

_DATA_PUBLICACAO = re.compile(r"\d{4}-\d{2}-\d{2}")
_INTERVALO = re.compile(r"\d{4}A\d{4}", re.IGNORECASE)
_ANO = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")


@dataclass(frozen=True)
class Resource:
    id: str
    package: str
    nome: str
    url: str
    ano: int
    tamanho: int | None
    modificado_em: str | None


def ano_do_recurso(nome: str) -> int | None:
    """Extrai o ano-base do nome do recurso.

    Os nomes seguem `BR-CAPES-<COLECAO>-[<INTERVALO>-]<DATA_PUBLICACAO>[_<ANO>]`
    ou `...-<ANO>-<DATA_PUBLICACAO>`. Remove a data de publicação e o
    intervalo do pacote (ex.: 2013A2016); o último ano restante é o ano-base.
    """
    limpo = _INTERVALO.sub("", _DATA_PUBLICACAO.sub("", nome))
    anos = _ANO.findall(limpo)
    return int(anos[-1]) if anos else None


def selecionar_csvs(pacote: dict, anos: tuple[int, int]) -> list[Resource]:
    inicio, fim = anos
    selecionados = []
    for r in pacote["resources"]:
        if (r.get("format") or "").upper() != "CSV":
            continue
        ano = ano_do_recurso(r["name"])
        if ano is None or not inicio <= ano <= fim:
            continue
        selecionados.append(
            Resource(
                id=r["id"],
                package=pacote["name"],
                nome=r["name"].strip(),
                url=r["url"],
                ano=ano,
                tamanho=r.get("size"),
                modificado_em=r.get("last_modified") or r.get("metadata_modified"),
            )
        )
    return sorted(selecionados, key=lambda r: (r.ano, r.nome))


def package_show(client: httpx.Client, ckan_url: str, package: str) -> dict:
    resp = client.get(f"{ckan_url}/api/3/action/package_show", params={"id": package})
    resp.raise_for_status()
    corpo = resp.json()
    if not corpo.get("success"):
        raise RuntimeError(f"CKAN package_show falhou para {package}: {corpo.get('error')}")
    return corpo["result"]
