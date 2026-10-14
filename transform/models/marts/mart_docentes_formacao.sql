-- Onde os docentes (pessoas distintas) obtiveram a maior titulação: país e, no Brasil, a IES.
-- Agregado por ano; IES identificada pela sigla informada.
with pessoas as (
    select distinct ano, id_pessoa, pais_titulacao, sg_ies_titulacao
    from {{ ref('stg_docentes') }}
)
select
    ano,
    coalesce(pais_titulacao, 'NÃO INFORMADO')                                as pais_titulacao,
    case when pais_titulacao = 'BRASIL' then coalesce(sg_ies_titulacao, 'NÃO INFORMADA') end as sg_ies_titulacao,
    count(*)                                                                as n_pessoas
from pessoas
group by all
