"""Helpers do site: leitura do capes_kb.sqlite e componentes HTML (stat tile, sparkline).

Usado pelos .qmd com `#| output: asis`. Sem JavaScript: o SVG usa variáveis CSS
(--viz-*) definidas em styles/*.scss, então tema claro/escuro vem de graça.
"""

import html
import os
import sqlite3
from functools import lru_cache
from pathlib import Path

SQLITE = Path(os.environ.get("CAPES_KB_SQLITE", Path(__file__).resolve().parents[1] / "data" / "capes_kb.sqlite"))


@lru_cache(maxsize=1)
def _con() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{SQLITE.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def consulta(sql: str, *params) -> list[sqlite3.Row]:
    return _con().execute(sql, params).fetchall()


def metadado(chave: str) -> str:
    return consulta("select valor from metadados where chave = ?", chave)[0]["valor"]


def modulos() -> list[sqlite3.Row]:
    return consulta("select modulo, nome from modulo order by modulo")


def indicadores(modulo: str | None = None) -> list[sqlite3.Row]:
    sql = "select * from indicador" + (" where modulo = ?" if modulo else "") + " order by modulo, rowid"
    return consulta(sql, *([modulo] if modulo else []))


def indicador(indicador_id: str) -> sqlite3.Row:
    return consulta("select * from indicador where indicador_id = ?", indicador_id)[0]


def serie(indicador_id: str, recorte_tipo: str = "brasil", recorte_valor: str = "BRASIL") -> list[tuple[int, float]]:
    rows = consulta(
        "select ano, valor from indicador_valor where indicador_id = ? and recorte_tipo = ? and recorte_valor = ? order by ano",
        indicador_id, recorte_tipo, recorte_valor,
    )
    return [(r["ano"], r["valor"]) for r in rows if r["valor"] is not None]


# ── formatação pt-BR ─────────────────────────────────────────────────────────

def _num(v: float, casas: int) -> str:
    s = f"{v:,.{casas}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def fmt(valor: float | None, unidade: str) -> str:
    if valor is None:
        return "—"
    if unidade == "contagem":
        return _num(valor, 0)
    if unidade == "percentual":
        return _num(valor, 1) + "%"
    if unidade == "meses":
        return _num(valor, 1) + " meses"
    if unidade == "indice" and abs(valor) >= 100:
        return _num(valor, 0)  # ex.: HHI 2.183
    return _num(valor, 1)


def fmt_delta(atual: float, anterior: float, unidade: str) -> str:
    """Percentuais variam em pontos percentuais; demais grandezas em %."""
    if unidade == "percentual":
        d, sufixo = atual - anterior, " p.p."
    elif anterior:
        d, sufixo = 100 * (atual / anterior - 1), "%"
    else:
        return ""
    seta = "▲" if d > 0.05 else "▼" if d < -0.05 else "■"
    return f"{seta} {'+' if d > 0 else ''}{_num(d, 1)}{sufixo}"


# ── componentes ──────────────────────────────────────────────────────────────

def sparkline(pontos: list[tuple[int, float]], unidade: str, largura: int = 220, altura: int = 56) -> str:
    """Linha 2px com marcador no último ponto; alvos de hover de 16px com <title> por ano."""
    if len(pontos) < 2:
        return ""
    px, py = 6, 8
    anos = [a for a, _ in pontos]
    vals = [v for _, v in pontos]
    vmin, vmax = min(vals), max(vals)
    amp = (vmax - vmin) or 1

    def x(a: int) -> float:
        return px + (a - anos[0]) / (anos[-1] - anos[0]) * (largura - 2 * px)

    def y(v: float) -> float:
        return altura - py - (v - vmin) / amp * (altura - 2 * py)

    caminho = " ".join(f"{'M' if i == 0 else 'L'}{x(a):.1f},{y(v):.1f}" for i, (a, v) in enumerate(pontos))
    alvos = "".join(
        f'<circle class="viz-hit" cx="{x(a):.1f}" cy="{y(v):.1f}" r="8">'
        f"<title>{a}: {html.escape(fmt(v, unidade))}</title></circle>"
        for a, v in pontos
    )
    ua, uv = pontos[-1]
    rotulo = f"Série {anos[0]}–{anos[-1]}, de {fmt(vals[0], unidade)} a {fmt(uv, unidade)}"
    return (
        f'<svg class="viz-spark" viewBox="0 0 {largura} {altura}" preserveAspectRatio="none" '
        f'role="img" aria-label="{html.escape(rotulo)}">'
        f'<path class="viz-line" d="{caminho}"/>'
        f'<circle class="viz-last" cx="{x(ua):.1f}" cy="{y(uv):.1f}" r="4"/>'
        f"{alvos}</svg>"
        f'<div class="viz-spark-anos"><span>{anos[0]}</span><span>{anos[-1]}</span></div>'
    )


def stat_tile(ind: sqlite3.Row, link: str | None = None) -> str:
    pontos = serie(ind["indicador_id"])
    if not pontos:
        return ""
    ano, valor = pontos[-1]
    delta = fmt_delta(valor, pontos[-2][1], ind["unidade"]) if len(pontos) > 1 else ""
    comparacao = f"vs {pontos[-2][0]} · " if len(pontos) > 1 else ""
    nome = html.escape(ind["nome"])
    titulo = f'<a href="{link}">{nome}</a>' if link else nome
    return (
        '<div class="kb-tile">'
        f'<div class="kb-tile-label">{titulo}</div>'
        f'<div class="kb-tile-value">{fmt(valor, ind["unidade"])}</div>'
        f'<div class="kb-tile-delta">{delta} <span class="kb-muted">{comparacao}Brasil, {ano}</span></div>'
        f'<div class="kb-tile-trend">{sparkline(pontos, ind["unidade"])}</div>'
        "</div>"
    )


def grade_tiles(inds: list[sqlite3.Row], link_catalogo: str = "") -> str:
    tiles = "".join(
        stat_tile(i, f"{link_catalogo}#ind-{i['indicador_id']}" if link_catalogo else None) for i in inds
    )
    return f'\n<div class="kb-grid">{tiles}</div>\n'


def tabela_serie(ind: sqlite3.Row) -> str:
    """Visão em tabela da série (acessibilidade e leitura exata)."""
    pontos = serie(ind["indicador_id"])
    cab = "".join(f"<th>{a}</th>" for a, _ in pontos)
    val = "".join(f"<td>{fmt(v, ind['unidade'])}</td>" for _, v in pontos)
    return (
        '<details class="kb-tabela"><summary>Ver valores por ano</summary>'
        f'<div class="table-responsive"><table class="table table-sm"><thead><tr>{cab}</tr></thead>'
        f"<tbody><tr>{val}</tr></tbody></table></div></details>"
    )
