-- Frequência de cada termo por quadriênio (2013–16, 2017–20, 2021–24), por 10 mil trabalhos,
-- para identificar temas emergentes e em queda. Só termos com ≥ 150 usos no período todo.
with base as (
    select
        case when ano <= 2016 then '2013–2016' when ano <= 2020 then '2017–2020' else '2021–2024' end as periodo,
        id_trabalho, chave, forma
    from {{ ref('int_teses_palavras_chave') }}
),
totais as (
    select periodo, count(distinct id_trabalho) as trabalhos_periodo from base group by periodo
),
termos as (
    select chave, mode(forma) as forma from base group by chave having count(*) >= 150
),
contagens as (
    select periodo, chave, count(*) as n from base group by periodo, chave
)
-- todo termo aparece nos três períodos (0 quando não usado), para não perder os que surgiram depois
select
    t.periodo,
    m.chave,
    m.forma,
    coalesce(c.n, 0)                                   as n_trabalhos,
    t.trabalhos_periodo,
    10000.0 * coalesce(c.n, 0) / t.trabalhos_periodo   as por_10_mil
from termos m
cross join totais t
left join contagens c on c.chave = m.chave and c.periodo = t.periodo
