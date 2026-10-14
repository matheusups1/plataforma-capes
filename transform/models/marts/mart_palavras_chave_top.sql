-- 30 palavras-chave mais frequentes por ano e grande área ('TODAS' = sistema inteiro).
-- n_trabalhos = trabalhos que usam o termo; forma = grafia mais comum (minúsculas, com acento).
with rotulados as (
    select ano,
           -- grouping() distingue o total geral de trabalhos sem grande área informada
           case when grouping(grande_area) = 1 then 'TODAS' else coalesce(grande_area, 'NÃO INFORMADA') end as grande_area,
           chave, mode(forma) as forma, count(*) as n_trabalhos
    from {{ ref('int_teses_palavras_chave') }}
    group by grouping sets ((ano, grande_area, chave), (ano, chave))
)
select *
from rotulados
qualify row_number() over (partition by ano, grande_area order by n_trabalhos desc, chave) <= 30
