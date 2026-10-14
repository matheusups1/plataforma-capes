-- Expectativa de atuação declarada pelos titulados, por ano e nível.
select ano, nivel, coalesce(expectativa_atuacao, 'NÃO INFORMADA') as expectativa, count(*) as n
from {{ ref('stg_teses') }}
where nivel is not null
group by all
