-- Indicadores do módulo 02 — Programas e avaliação (ver indicators/indicadores.yml).
with programas as (
    select r.*, f.conceito as nota, f.oferta_doutorado, f.em_rede
    from {{ ref('int_programa_recortes') }} r
    join {{ ref('fct_programa_ano') }} f using (cd_programa, ano)
)
{{ pct_por_recortes('prog_pct_nota_5_mais', 'programas',
    'count(*) filter (where nota >= 5)', 'count(nota)') }}
union all
{{ razao_por_recortes('prog_conceito_medio', 'programas', 'sum(nota)', 'count(nota)') }}
union all
{{ pct_por_recortes('prog_pct_com_doutorado', 'programas',
    'count(*) filter (where oferta_doutorado)', 'count(*)') }}
union all
{{ pct_por_recortes('prog_pct_profissional', 'programas',
    "count(*) filter (where modalidade = 'PROFISSIONAL')", 'count(*)') }}
union all
{{ pct_por_recortes('prog_pct_em_rede', 'programas',
    'count(*) filter (where em_rede)', 'count(*)') }}
