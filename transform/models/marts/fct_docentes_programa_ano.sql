-- Grão: programa × ano. Contagens de vínculos docentes (uma pessoa pode ter vínculo em
-- mais de um programa; para pessoas distintas use stg_docentes com count(distinct)).
-- Endogenia: permanente doutorado na mesma IES do programa, comparando siglas (a sigla da
-- IES do programa é a vigente naquele ano). Siglas grafadas de outro modo não casam, então
-- a medida tende a subestimar.
select
    d.ano,
    d.cd_programa,
    count(*)                                                     as n_vinculos,
    count(*) filter (where d.categoria = 'PERMANENTE')           as n_permanentes,
    count(*) filter (where d.categoria = 'COLABORADOR')          as n_colaboradores,
    count(*) filter (where d.categoria = 'VISITANTE')            as n_visitantes,
    count(*) filter (where d.doutor)                             as n_doutores,
    count(*) filter (where d.bolsa_produtividade_cnpq is not null) as n_bolsa_pq,
    count(*) filter (where d.titulado_exterior)                  as n_titulados_exterior,
    count(*) filter (where d.estrangeiro)                        as n_estrangeiros,
    count(*) filter (where d.regime_trabalho = 'DEDICAÇÃO EXCLUSIVA') as n_dedicacao_exclusiva,
    count(*) filter (where d.ano - d.ano_nascimento >= 60)       as n_60_mais,
    count(d.ano_nascimento)                                      as n_com_idade,
    count(*) filter (where d.categoria = 'PERMANENTE' and d.sg_ies_titulacao is not null)
                                                                 as n_permanentes_com_ies_titulacao,
    count(*) filter (where d.categoria = 'PERMANENTE' and d.sg_ies_titulacao = p.sg_ies)
                                                                 as n_permanentes_endogenos
from {{ ref('stg_docentes') }} d
join {{ ref('stg_programas') }} p using (cd_programa, ano)
group by d.ano, d.cd_programa
