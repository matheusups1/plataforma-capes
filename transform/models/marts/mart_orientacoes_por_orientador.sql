-- Distribuição de defesas orientadas por orientador no ano (catálogo de teses).
-- Grão: ano × número de defesas (10 = 10 ou mais) → quantos orientadores e quantos trabalhos.
with por_orientador as (
    select ano, id_pessoa_orientador, count(*) as n
    from {{ ref('stg_teses') }}
    where id_pessoa_orientador is not null
    group by all
)
select
    ano,
    least(n, 10)  as defesas_orientadas,
    count(*)      as n_orientadores,
    sum(n)        as n_trabalhos
from por_orientador
group by all
