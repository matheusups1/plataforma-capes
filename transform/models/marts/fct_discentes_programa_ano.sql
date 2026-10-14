-- Grão: programa × nível × ano. Situação ao fim do ano-base:
-- titulados/desligados são eventos do ano; matriculados é o estoque em 31/12.
select
    ano,
    cd_programa,
    nivel,
    eh_doutorado,
    count(*)                                                        as n_vinculos,
    count(*) filter (where situacao = 'MATRICULADO')                as n_matriculados,
    count(*) filter (where situacao = 'TITULADO')                   as n_titulados,
    count(*) filter (where situacao in ('DESLIGADO', 'ABANDONOU'))  as n_desligados,
    count(*) filter (where situacao = 'MUDANÇA DE NÍVEL SEM DEFESA') as n_mudanca_nivel,
    count(*) filter (where ingressante)                             as n_ingressantes,
    count(*) filter (where estrangeiro)                             as n_estrangeiros,
    sum(meses_ate_titulacao)                                        as soma_meses_titulacao,
    count(meses_ate_titulacao)                                      as n_com_meses_titulacao
from {{ ref('stg_discentes') }}
group by ano, cd_programa, nivel, eh_doutorado
