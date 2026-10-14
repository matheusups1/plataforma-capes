-- Indicadores do módulo 05 — Teses e dissertações (ver indicators/indicadores.yml).
with teses as (
    select r.*, f.eh_doutorado, f.n_trabalhos, f.n_em_ingles, f.soma_paginas, f.n_com_paginas
    from {{ ref('fct_teses_programa_ano') }} f
    join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
)
{{ por_recortes('tes_total', 'teses', 'sum(n_trabalhos)') }}
union all
{{ por_recortes('tes_teses_doutorado', 'teses', 'sum(n_trabalhos) filter (where eh_doutorado)') }}
union all
{{ pct_por_recortes('tes_pct_ingles', 'teses', 'sum(n_em_ingles)', 'sum(n_trabalhos)') }}
union all
{{ razao_por_recortes('tes_paginas_media', 'teses', 'sum(soma_paginas)', 'sum(n_com_paginas)') }}
