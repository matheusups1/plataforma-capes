-- Indicadores do módulo 03 — Docentes (ver indicators/indicadores.yml).
with vinculos as (            -- grão pessoa × programa × ano (para pessoas distintas)
    select r.*, d.id_pessoa, d.categoria
    from {{ ref('stg_docentes') }} d
    join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
),
programas as (                -- grão programa × ano (para razões entre fatos)
    select
        r.*,
        d.n_vinculos, d.n_permanentes, d.n_bolsa_pq, d.n_titulados_exterior,
        d.n_60_mais, d.n_com_idade, d.n_permanentes_endogenos, d.n_permanentes_com_ies_titulacao,
        dc.n_matriculados
    from {{ ref('int_programa_recortes') }} r
    join {{ ref('fct_docentes_programa_ano') }} d using (cd_programa, ano)
    left join (
        select cd_programa, ano, sum(n_matriculados) as n_matriculados
        from {{ ref('fct_discentes_programa_ano') }}
        group by all
    ) dc using (cd_programa, ano)
),
pais as (                     -- denominador do % exterior: vínculos com país informado
    select r.*, d.titulado_exterior
    from {{ ref('stg_docentes') }} d
    join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
    where d.pais_titulacao is not null
)
{{ por_recortes('doc_total', 'vinculos', 'count(distinct id_pessoa)') }}
union all
{{ por_recortes('doc_permanentes', 'vinculos',
    "count(distinct id_pessoa) filter (where categoria = 'PERMANENTE')") }}
union all
{{ pct_por_recortes('doc_pct_permanentes', 'programas', 'sum(n_permanentes)', 'sum(n_vinculos)') }}
union all
{{ razao_por_recortes('doc_por_programa', 'programas', 'sum(n_vinculos)', 'count(*)') }}
union all
{{ pct_por_recortes('doc_pct_bolsa_pq', 'programas', 'sum(n_bolsa_pq)', 'sum(n_vinculos)') }}
union all
{{ pct_por_recortes('doc_pct_titulado_exterior', 'pais',
    'count(*) filter (where titulado_exterior)', 'count(*)') }}
union all
{{ pct_por_recortes('doc_pct_60_mais', 'programas', 'sum(n_60_mais)', 'sum(n_com_idade)') }}
union all
{{ pct_por_recortes('doc_pct_endogenia', 'programas',
    'sum(n_permanentes_endogenos)', 'sum(n_permanentes_com_ies_titulacao)') }}
union all
{{ razao_por_recortes('doc_razao_discente_docente', 'programas',
    'sum(n_matriculados)', 'sum(n_permanentes)') }}
