-- Docentes (pessoas distintas) por faixa de idade, ano e categoria. Agregado nacional.
with pessoas as (
    select distinct ano, id_pessoa, ano - ano_nascimento as idade,
           -- quem é permanente em algum programa conta como permanente
           max(categoria = 'PERMANENTE') over (partition by ano, id_pessoa) as permanente
    from {{ ref('stg_docentes') }}
)
select
    ano,
    permanente,
    case
        when idade is null or idade < 20 or idade > 100 then 'não informada'
        when idade < 40 then 'até 39'
        when idade < 50 then '40 a 49'
        when idade < 60 then '50 a 59'
        when idade < 70 then '60 a 69'
        else '70 ou mais'
    end      as faixa_idade,
    count(*) as n_pessoas
from pessoas
group by all
