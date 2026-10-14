-- Áreas de avaliação com o nome mais recente (9 áreas foram renomeadas entre 2013 e 2024).
select
    cd_area_avaliacao,
    arg_max(nm_area_avaliacao, ano) as nm_area_avaliacao,
    arg_max(grande_area, ano)       as grande_area,
    list(distinct nm_area_avaliacao order by nm_area_avaliacao) as nomes_historicos,
    min(ano)                        as primeiro_ano,
    max(ano)                        as ultimo_ano
from {{ ref('stg_programas') }}
group by cd_area_avaliacao
