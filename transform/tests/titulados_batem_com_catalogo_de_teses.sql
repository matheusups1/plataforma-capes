-- Coerência entre fontes: discentes TITULADOS no ano devem corresponder aos trabalhos
-- do catálogo de teses daquele ano. Diferença observada: 1 trabalho em 2015.
-- Falha se a divergência passar de 0,1% em algum ano.
with titulados as (
    select ano, count(*) as n from {{ ref('stg_discentes') }} where situacao = 'TITULADO' group by ano
), teses as (
    select ano, count(*) as n from {{ ref('stg_teses') }} group by ano
)
select t.ano, t.n as titulados, c.n as teses
from titulados t full join teses c using (ano)
where abs(coalesce(t.n, 0) - coalesce(c.n, 0)) > 0.001 * greatest(t.n, c.n)
