-- Todo indicador do catálogo precisa ter valores para todos os anos no recorte Brasil.
-- (A direção inversa — valor sem documentação — é o teste de relationships no mart.)
with anos as (select distinct ano from {{ ref('stg_programas') }})
select i.indicador_id, a.ano
from {{ ref('indicadores') }} i
cross join anos a
anti join {{ ref('mart_indicador_valor') }} v
    on v.indicador_id = i.indicador_id and v.ano = a.ano and v.recorte_tipo = 'brasil'
