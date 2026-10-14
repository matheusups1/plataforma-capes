-- Grão: programa × ano. Contagens de vínculos docentes (uma pessoa pode ter vínculo em
-- mais de um programa; para pessoas distintas use stg_docentes com count(distinct)).
select
    ano,
    cd_programa,
    count(*)                                                   as n_vinculos,
    count(*) filter (where categoria = 'PERMANENTE')           as n_permanentes,
    count(*) filter (where categoria = 'COLABORADOR')          as n_colaboradores,
    count(*) filter (where categoria = 'VISITANTE')            as n_visitantes,
    count(*) filter (where doutor)                             as n_doutores,
    count(*) filter (where bolsa_produtividade_cnpq is not null) as n_bolsa_pq,
    count(*) filter (where titulado_exterior)                  as n_titulados_exterior,
    count(*) filter (where estrangeiro)                        as n_estrangeiros,
    count(*) filter (where regime_trabalho = 'DEDICAÇÃO EXCLUSIVA') as n_dedicacao_exclusiva
from {{ ref('stg_docentes') }}
group by ano, cd_programa
