-- Formato longo único consumido pelo site: um valor por indicador × ano × recorte.
-- A documentação de cada indicador está no seed `indicadores` (de indicators/indicadores.yml).
with valores as (
    {% for m in ['mart_ind_01_sistema', 'mart_ind_02_programas', 'mart_ind_03_docentes',
                 'mart_ind_04_discentes', 'mart_ind_05_teses'] -%}
    select * from {{ ref(m) }}
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
),
completos as (
    select
        v.indicador_id,
        v.ano,
        v.recorte_tipo,
        v.recorte_valor,
        -- contagem sem ocorrências no recorte é zero, não ausência de dado
        case when i.unidade = 'contagem' then coalesce(v.valor, 0) else v.valor end as valor,
        v.numerador,
        v.denominador,
        i.unidade
    from valores v
    join {{ ref('indicadores') }} i using (indicador_id)
)
select
    *,
    case when lag(ano) over w = ano - 1 and lag(valor) over w <> 0
         then 100.0 * (valor / lag(valor) over w - 1) end as variacao_anual_pct
from completos
window w as (partition by indicador_id, recorte_tipo, recorte_valor order by ano)
