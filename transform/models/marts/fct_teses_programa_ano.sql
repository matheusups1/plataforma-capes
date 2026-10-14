-- Grão: programa × nível × ano de defesa.
select
    ano,
    cd_programa,
    nivel,
    coalesce(eh_doutorado, false)                         as eh_doutorado,
    count(*)                                              as n_trabalhos,
    count(*) filter (where idioma = 'INGLES')             as n_em_ingles,
    sum(paginas) filter (where paginas between 1 and 2000) as soma_paginas,
    count(*) filter (where paginas between 1 and 2000)    as n_com_paginas
from {{ ref('stg_teses') }}
group by all
