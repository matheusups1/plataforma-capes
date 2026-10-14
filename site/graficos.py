"""Gráficos dos módulos em SVG/HTML estático, temáveis por variáveis CSS (sem JavaScript).

Cores por papel (definidas em styles/light.scss e styles/dark.scss, validadas):
  --viz-s1..s5  categórica (identidade: regiões, séries)
  --viz-o1..o5  ordinal (notas ≤3 → 7), --viz-neutro (sem nota)
Toda marca tem <title> (tooltip) e todo gráfico deve vir com `tabela()` como visão alternativa.
"""

import html
import math

from kb import fmt

CATEGORICA = [f"var(--viz-s{i})" for i in range(1, 6)]


def ticks(lo: float, hi: float, alvo: int = 5) -> list[float]:
    """Marcas "redondas" (1, 2, 5 × 10^n) cobrindo [lo, hi]."""
    if hi <= lo:
        hi = lo + 1
    bruto = (hi - lo) / alvo
    mag = 10 ** math.floor(math.log10(bruto))
    passo = next(m * mag for m in (1, 2, 5, 10) if m * mag >= bruto)
    ini, fim = math.floor(lo / passo) * passo, math.ceil(hi / passo) * passo
    n = round((fim - ini) / passo)
    return [round(ini + i * passo, 10) for i in range(n + 1)]


def _num_eixo(v: float, unidade: str) -> str:
    """Marcas de eixo inteiras sem casas decimais ("50%", "4.000")."""
    if float(v).is_integer():
        texto = fmt(v, "contagem")
        return texto + "%" if unidade == "percentual" else texto
    return fmt(v, unidade).replace(" meses", "")


def legenda(itens: list[tuple[str, str]]) -> str:
    sw = "".join(
        f'<span class="viz-legenda-item"><span class="viz-swatch" style="background:{cor}"></span>{html.escape(n)}</span>'
        for n, cor in itens
    )
    return f'<div class="viz-legenda">{sw}</div>'


def linhas(series: list[tuple[str, list[tuple[int, float]]]], unidade: str,
           zero: bool = True, rotulo: str = "") -> str:
    """Séries temporais: linha 2px, rótulo direto no fim (com guia se precisou deslocar),
    alvo de hover por ponto e legenda (sempre que houver ≥ 2 séries)."""
    W, H, ml, mr, mt, mb = 560, 260, 52, 128, 12, 26
    anos = sorted({a for _, pts in series for a, _ in pts})
    vals = [v for _, pts in series for _, v in pts if v is not None]
    marcas = ticks(0 if zero else min(vals), max(vals))
    y0, y1 = marcas[0], marcas[-1]

    def x(a):
        return ml + (a - anos[0]) / max(anos[-1] - anos[0], 1) * (W - ml - mr)

    def y(v):
        return mt + (1 - (v - y0) / (y1 - y0)) * (H - mt - mb)

    partes = []
    for m in marcas:
        partes.append(f'<line class="viz-grade" x1="{ml}" x2="{W - mr}" y1="{y(m):.1f}" y2="{y(m):.1f}"/>')
        partes.append(f'<text class="viz-eixo" x="{ml - 6}" y="{y(m) + 4:.1f}" text-anchor="end">{_num_eixo(m, unidade)}</text>')
    for a in anos:
        if a in (anos[0], anos[-1]) or len(anos) <= 12:
            partes.append(f'<text class="viz-eixo" x="{x(a):.1f}" y="{H - 6}" text-anchor="middle">{a}</text>')

    fins = []
    for i, (nome, pts) in enumerate(series):
        cor = CATEGORICA[i % len(CATEGORICA)]
        pts = [(a, v) for a, v in pts if v is not None]
        d = " ".join(f"{'M' if j == 0 else 'L'}{x(a):.1f},{y(v):.1f}" for j, (a, v) in enumerate(pts))
        partes.append(f'<path class="viz-serie" d="{d}" style="stroke:{cor}"/>')
        a_fim, v_fim = pts[-1]
        partes.append(f'<circle class="viz-ponto-fim" cx="{x(a_fim):.1f}" cy="{y(v_fim):.1f}" r="4" style="fill:{cor}"/>')
        for a, v in pts:
            partes.append(
                f'<circle class="viz-hit" cx="{x(a):.1f}" cy="{y(v):.1f}" r="7">'
                f"<title>{html.escape(nome)} · {a}: {html.escape(fmt(v, unidade))}</title></circle>"
            )
        fins.append([y(v_fim), y(v_fim), nome, v_fim])

    # rótulos diretos: espaçamento mínimo de 14px; se deslocado, guia fina até a linha
    fins.sort(key=lambda f: f[0])
    for k in range(1, len(fins)):
        fins[k][1] = max(fins[k][1], fins[k - 1][1] + 14)
    excesso = fins[-1][1] - (H - mb) if fins else 0
    if excesso > 0:
        for f in fins:
            f[1] -= excesso
    xf = W - mr
    for y_real, y_rot, nome, v in fins:
        if abs(y_rot - y_real) > 1:
            partes.append(f'<line class="viz-guia" x1="{xf + 4}" y1="{y_real:.1f}" x2="{xf + 12}" y2="{y_rot:.1f}"/>')
        partes.append(
            f'<text class="viz-rotulo-fim" x="{xf + 14}" y="{y_rot + 4:.1f}">'
            f"{html.escape(nome)} <tspan class=\"viz-rotulo-valor\">{html.escape(fmt(v, unidade))}</tspan></text>"
        )

    leg = legenda([(n, CATEGORICA[i % len(CATEGORICA)]) for i, (n, _) in enumerate(series)]) if len(series) > 1 else ""
    aria = html.escape(rotulo or ", ".join(n for n, _ in series))
    svg = f'<svg class="viz-grafico" viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">{"".join(partes)}</svg>'
    return f'<figure class="viz-fig">{leg}{svg}</figure>'


def barras_h(itens: list[tuple[str, float]], unidade: str, destaque: set[str] | None = None) -> str:
    """Barras horizontais em HTML (responsivas), ordenadas como recebidas; valor rotulado no fim."""
    vmax = max(v for _, v in itens) or 1
    linhas_html = []
    for nome, v in itens:
        classe = "viz-barra viz-barra-destaque" if destaque and nome in destaque else "viz-barra"
        valor = html.escape(fmt(v, unidade))
        linhas_html.append(
            f'<div class="viz-barra-rotulo">{html.escape(nome)}</div>'
            f'<div class="viz-barra-trilho" title="{html.escape(nome)}: {valor}">'
            f'<div class="{classe}" style="width:{100 * v / vmax:.2f}%"></div></div>'
            f'<div class="viz-barra-valor">{valor}</div>'
        )
    return f'<div class="viz-barras">{"".join(linhas_html)}</div>'


def colunas_empilhadas(anos: list[int], categorias: list[tuple[str, str]],
                       valores: dict[str, dict[int, float]], rotulo: str = "") -> str:
    """Colunas 100% empilhadas (composição por ano). Segmentos separados por 2px da superfície."""
    W, H, ml, mr, mt, mb = 560, 240, 40, 8, 10, 26
    largura_col = (W - ml - mr) / len(anos)
    barra = largura_col * 0.72
    partes = []
    for p in (0, 25, 50, 75, 100):
        yy = mt + (1 - p / 100) * (H - mt - mb)
        partes.append(f'<line class="viz-grade" x1="{ml}" x2="{W - mr}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        partes.append(f'<text class="viz-eixo" x="{ml - 6}" y="{yy + 4:.1f}" text-anchor="end">{p}%</text>')
    for i, a in enumerate(anos):
        total = sum(valores[c].get(a, 0) for c, _ in categorias) or 1
        x0 = ml + i * largura_col + (largura_col - barra) / 2
        base = H - mb
        for nome, cor in categorias:
            v = valores[nome].get(a, 0)
            if not v:
                continue
            h = v / total * (H - mt - mb)
            base -= h
            partes.append(
                f'<rect class="viz-segmento" x="{x0:.1f}" y="{base:.1f}" width="{barra:.1f}" height="{h:.1f}" style="fill:{cor}">'
                f"<title>{a} · {html.escape(nome)}: {fmt(v, 'contagem')} ({fmt(100 * v / total, 'percentual')})</title></rect>"
            )
        partes.append(f'<text class="viz-eixo" x="{x0 + barra / 2:.1f}" y="{H - 6}" text-anchor="middle">{str(a)[2:] if len(anos) > 8 else a}</text>')
    aria = html.escape(rotulo or "Composição por ano")
    svg = f'<svg class="viz-grafico" viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">{"".join(partes)}</svg>'
    return f'<figure class="viz-fig">{legenda(categorias)}{svg}</figure>'


def matriz(rotulos_linhas: list[str], rotulos_colunas: list[str], valores: list[list[int]],
           rotulo_linhas: str, rotulo_colunas: str) -> str:
    """Tabela de contagens com intensidade sequencial (q0 = zero, q1..q5 = proporcional ao máximo)."""
    vmax = max(max(l) for l in valores) or 1
    cab = "".join(f"<th>{html.escape(c)}</th>" for c in rotulos_colunas)
    corpo = []
    for nome, linha in zip(rotulos_linhas, valores):
        celulas = "".join(
            f'<td class="viz-q{0 if v == 0 else math.ceil(5 * v / vmax)}" title="{html.escape(nome)} → {html.escape(c)}: {v}">{v}</td>'
            for c, v in zip(rotulos_colunas, linha)
        )
        corpo.append(f"<tr><th>{html.escape(nome)}</th>{celulas}</tr>")
    return (
        '<div class="table-responsive"><table class="viz-matriz">'
        f'<thead><tr><th class="viz-matriz-canto">{html.escape(rotulo_linhas)} ↓ · {html.escape(rotulo_colunas)} →</th>{cab}</tr></thead>'
        f"<tbody>{''.join(corpo)}</tbody></table></div>"
    )


def tabela(cabecalho: list[str], linhas_tab: list[list[str]], resumo: str = "Ver dados em tabela") -> str:
    cab = "".join(f"<th>{html.escape(str(c))}</th>" for c in cabecalho)
    corpo = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in l) + "</tr>" for l in linhas_tab)
    return (
        f'<details class="kb-tabela"><summary>{html.escape(resumo)}</summary>'
        f'<div class="table-responsive"><table class="table table-sm"><thead><tr>{cab}</tr></thead>'
        f"<tbody>{corpo}</tbody></table></div></details>"
    )
