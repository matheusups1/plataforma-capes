-- Instituições com atributos do ano mais recente em que tiveram programa.
-- (Algumas mudaram de natureza jurídica, ex. estadual → federal; o histórico fica em fct_programa_ano.)
select
    cd_ies,
    arg_max(sg_ies, ano)                 as sg_ies,
    arg_max(nm_ies, ano)                 as nm_ies,
    arg_max(status_juridico, ano)        as status_juridico,
    arg_max(dependencia_adm, ano)        as dependencia_adm,
    arg_max(organizacao_academica, ano)  as organizacao_academica,
    arg_max(regiao, ano)                 as regiao,
    arg_max(uf, ano)                     as uf,
    arg_max(municipio, ano)              as municipio,
    min(ano)                             as primeiro_ano,
    max(ano)                             as ultimo_ano
from {{ ref('stg_programas') }}
group by cd_ies
