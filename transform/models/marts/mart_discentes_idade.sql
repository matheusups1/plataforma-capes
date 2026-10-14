-- Faixa de idade (ano-base − ano de nascimento) de ingressantes e titulados, por ano × nível.
-- Agregado nacional; faixas próprias para manter os mesmos cortes em todos os anos.
with base as (
    select ano, nivel, 'ingressante' as evento, ano - ano_nascimento as idade
    from {{ ref('stg_discentes') }} where ingressante
    union all
    select ano, nivel, 'titulado', ano - ano_nascimento
    from {{ ref('stg_discentes') }} where situacao = 'TITULADO'
)
select
    ano,
    nivel,
    evento,
    case
        when idade is null or idade < 18 or idade > 90 then 'não informada'
        when idade < 25 then 'até 24'
        when idade < 30 then '25 a 29'
        when idade < 35 then '30 a 34'
        when idade < 40 then '35 a 39'
        when idade < 45 then '40 a 44'
        else '45 ou mais'
    end      as faixa_idade,
    count(*) as n
from base
group by all
