-- Distribuição dos meses entre matrícula e titulação, por ano × nível × grande área.
-- Agregado (sem pessoas): permite histogramas e percentis no site. Acima de 120 meses agrupa em 120.
select
    d.ano,
    d.nivel,
    r.grande_area,
    least(d.meses_ate_titulacao, 120) as meses,
    count(*)                          as n
from {{ ref('stg_discentes') }} d
join {{ ref('int_programa_recortes') }} r using (cd_programa, ano)
where d.situacao = 'TITULADO' and d.meses_ate_titulacao is not null
group by all
