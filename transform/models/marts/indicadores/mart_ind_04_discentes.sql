-- Indicadores do módulo 04 — Discentes e titulação (ver indicators/indicadores.yml).
with discentes as (
    select r.*, f.nivel, f.eh_doutorado,
           f.n_vinculos, f.n_matriculados, f.n_titulados, f.n_desligados,
           f.n_ingressantes, f.n_estrangeiros, f.soma_meses_titulacao, f.n_com_meses_titulacao,
           f.n_titulados_no_prazo
    from {{ ref('fct_discentes_programa_ano') }} f
    join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
)
{{ por_recortes('disc_matriculados', 'discentes', 'sum(n_matriculados)') }}
union all
{{ por_recortes('disc_ingressantes', 'discentes', 'sum(n_ingressantes)') }}
union all
{{ por_recortes('disc_titulados', 'discentes', 'sum(n_titulados)') }}
union all
{{ por_recortes('disc_titulados_doutorado', 'discentes',
    'sum(n_titulados) filter (where eh_doutorado)') }}
union all
{{ pct_por_recortes('disc_taxa_desligamento', 'discentes', 'sum(n_desligados)', 'sum(n_vinculos)') }}
union all
{{ razao_por_recortes('disc_tempo_titulacao_mestrado', 'discentes',
    "sum(soma_meses_titulacao) filter (where nivel = 'MESTRADO')",
    "sum(n_com_meses_titulacao) filter (where nivel = 'MESTRADO')") }}
union all
{{ razao_por_recortes('disc_tempo_titulacao_doutorado', 'discentes',
    "sum(soma_meses_titulacao) filter (where nivel = 'DOUTORADO')",
    "sum(n_com_meses_titulacao) filter (where nivel = 'DOUTORADO')") }}
union all
{{ pct_por_recortes('disc_pct_mestrado_no_prazo', 'discentes',
    "sum(n_titulados_no_prazo) filter (where nivel = 'MESTRADO')",
    "sum(n_com_meses_titulacao) filter (where nivel = 'MESTRADO')") }}
union all
{{ pct_por_recortes('disc_pct_doutorado_no_prazo', 'discentes',
    "sum(n_titulados_no_prazo) filter (where nivel = 'DOUTORADO')",
    "sum(n_com_meses_titulacao) filter (where nivel = 'DOUTORADO')") }}
union all
{{ pct_por_recortes('disc_pct_estrangeiros', 'discentes', 'sum(n_estrangeiros)', 'sum(n_vinculos)') }}
