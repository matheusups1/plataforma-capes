-- Indicadores do módulo 01 — Sistema de pós-graduação (ver indicators/indicadores.yml).
with programas as (
    select r.*, f.cd_ies
    from {{ ref('int_programa_recortes') }} r
    join {{ ref('fct_programa_ano') }} f using (cd_programa, ano)
),
cursos as (
    select r.*, c.eh_doutorado
    from {{ ref('stg_cursos') }} c
    join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
)
{{ por_recortes('prog_total', 'programas', 'count(*)') }}
union all
{{ por_recortes('curso_total', 'cursos', 'count(*)') }}
union all
{{ por_recortes('curso_doutorado_total', 'cursos', 'count(*) filter (where eh_doutorado)') }}
union all
{{ por_recortes('ies_total', 'programas', 'count(distinct cd_ies)') }}
