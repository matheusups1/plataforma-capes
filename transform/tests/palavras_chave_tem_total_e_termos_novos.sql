-- Regressões: (1) o top precisa ter o total geral 'TODAS' em todo ano;
-- (2) a tendência precisa manter termos sem uso no 1º período (ex.: covid-19).
select 'sem TODAS' as problema, ano::varchar as detalhe
from (select distinct ano from {{ ref('mart_palavras_chave_top') }}) a
where not exists (select 1 from {{ ref('mart_palavras_chave_top') }} t where t.ano = a.ano and t.grande_area = 'TODAS')
union all
select 'termo novo ausente', 'covid-19'
where not exists (select 1 from {{ ref('mart_palavras_chave_tendencia') }}
                  where chave = 'covid-19' and periodo = '2013–2016' and n_trabalhos = 0)
