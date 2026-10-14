-- Vínculos discente × programa × nível × ano-base, com a situação no fim do ano.
-- PRIVACIDADE: nome, documento, orientador e título são descartados; id_pessoa é pseudônimo.
-- QUALIDADE: 2 registros duplicados na fonte (mesma pessoa com duas matrículas no mesmo
-- curso/ano); mantemos a matrícula mais recente. ~930 titulados (0,1%) têm 0 meses até a
-- titulação, o que é impossível: viram NULL para não distorcer médias e percentis.
with fonte as (
    select *
    from {{ source('bronze', 'discentes') }}
    qualify row_number() over (
        partition by ID_PESSOA, CD_PROGRAMA_IES, DS_GRAU_ACADEMICO_DISCENTE, _ano
        order by {{ data_capes('DT_MATRICULA_DISCENTE') }} desc
    ) = 1
)
select
    _ano::integer                                          as ano,
    ID_PESSOA                                              as id_pessoa,
    CD_PROGRAMA_IES                                        as cd_programa,
    CD_ENTIDADE_CAPES                                      as cd_ies,
    CD_AREA_AVALIACAO::integer                             as cd_area_avaliacao,
    NM_MODALIDADE_PROGRAMA                                 as modalidade,
    NM_REGIAO                                              as regiao,
    SG_UF_PROGRAMA                                         as uf,
    DS_DEPENDENCIA_ADMINISTRATIVA                          as dependencia_adm,

    DS_GRAU_ACADEMICO_DISCENTE                             as nivel,
    DS_GRAU_ACADEMICO_DISCENTE like 'DOUTORADO%'           as eh_doutorado,
    -- a fonte grafa "MUDANÇA" com e sem cedilha
    replace(NM_SITUACAO_DISCENTE, 'MUDANCA', 'MUDANÇA')    as situacao,
    ST_INGRESSANTE = 'SIM'                                 as ingressante,
    {{ data_capes('DT_MATRICULA_DISCENTE') }}              as dt_matricula,
    {{ data_capes('DT_SITUACAO_DISCENTE') }}               as dt_situacao,
    case when NM_SITUACAO_DISCENTE = 'TITULADO' and try_cast(QT_MES_TITULACAO as integer) > 0
         then try_cast(QT_MES_TITULACAO as integer) end    as meses_ate_titulacao,

    try_cast(AN_NASCIMENTO_DISCENTE as integer)            as ano_nascimento,
    {{ nulo('DS_FAIXA_ETARIA') }}                          as faixa_etaria,
    DS_TIPO_NACIONALIDADE_DISCENTE = 'ESTRANGEIRO'         as estrangeiro,
    {{ nulo('NM_PAIS_NACIONALIDADE_DISCENTE') }}           as pais_nacionalidade
from fonte
