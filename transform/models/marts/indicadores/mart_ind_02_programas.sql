-- Indicadores do módulo 02 — Programas e avaliação (ver indicators/indicadores.yml).
with programas as (
    select r.*, f.conceito as nota, f.oferta_doutorado, f.em_rede
    from {{ ref('int_programa_recortes') }} r
    join {{ ref('fct_programa_ano') }} f using (cd_programa, ano)
),
-- HHI: concentração dos programas entre UFs, dentro de cada recorte não geográfico.
-- (Recortes regiao/uf não se aplicam: dentro de uma UF a concentração é trivialmente 10.000.)
hhi_contagens as (
    select ano, 'brasil' as recorte_tipo, 'BRASIL' as recorte_valor, uf, count(*) as n
    from programas group by all
    {%- for r in ['grande_area', 'area_avaliacao', 'modalidade', 'dependencia_adm', 'conceito'] %}
    union all
    select ano, '{{ r }}', {{ r }}::varchar, uf, count(*) from programas group by all
    {%- endfor %}
),
hhi_participacoes as (
    select ano, recorte_tipo, recorte_valor,
           n::double / sum(n) over (partition by ano, recorte_tipo, recorte_valor) as participacao
    from hhi_contagens
),
hhi as (
    select 'prog_hhi_uf' as indicador_id, ano, recorte_tipo, recorte_valor,
           10000 * sum(participacao * participacao) as valor,
           null::double as numerador, null::double as denominador
    from hhi_participacoes
    group by ano, recorte_tipo, recorte_valor
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
union all
select * from hhi
