-- Atributos de recorte de cada programa × ano, usados por todos os indicadores.
-- Fatos de docentes/discentes/teses usam estes atributos (e não os da própria fonte)
-- para que todos os indicadores recortem a mesma população da mesma forma.
select
    p.ano,
    p.cd_programa,
    p.regiao,
    p.uf,
    p.grande_area,
    a.nm_area_avaliacao                          as area_avaliacao,  -- nome vigente
    p.modalidade,
    p.dependencia_adm,
    coalesce(p.conceito::varchar, 'A')           as conceito          -- 'A' = em implantação
from {{ ref('stg_programas') }} p
join {{ ref('dim_area_avaliacao') }} a using (cd_area_avaliacao)
