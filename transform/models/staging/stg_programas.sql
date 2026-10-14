-- Um registro por programa × ano-base, colunas tipadas e harmonizadas entre períodos.
-- 2013–2016 usam ANO_INICIO_PROGRAMA; 2017+ usam AN_INICIO_PROGRAMA.
select
    _ano::integer                                              as ano,
    CD_PROGRAMA_IES                                            as cd_programa,
    NM_PROGRAMA_IES                                            as nm_programa,
    {{ nulo('NM_PROGRAMA_IDIOMA') }}                           as nm_programa_ingles,

    CD_ENTIDADE_CAPES                                          as cd_ies,
    {{ nulo('CD_ENTIDADE_EMEC') }}                             as cd_ies_emec,
    SG_ENTIDADE_ENSINO                                         as sg_ies,
    NM_ENTIDADE_ENSINO                                         as nm_ies,
    CS_STATUS_JURIDICO                                         as status_juridico,
    DS_DEPENDENCIA_ADMINISTRATIVA                              as dependencia_adm,
    nullif({{ nulo('DS_ORGANIZACAO_ACADEMICA') }}, 'NÃO INFORMADO') as organizacao_academica,

    NM_REGIAO                                                  as regiao,
    SG_UF_PROGRAMA                                             as uf,
    NM_MUNICIPIO_PROGRAMA_IES                                  as municipio,

    CD_AREA_AVALIACAO::integer                                 as cd_area_avaliacao,
    NM_AREA_AVALIACAO                                          as nm_area_avaliacao,
    NM_GRANDE_AREA_CONHECIMENTO                                as grande_area,
    NM_AREA_CONHECIMENTO                                       as area_conhecimento,
    {{ nulo('NM_SUBAREA_CONHECIMENTO') }}                      as subarea_conhecimento,

    NM_MODALIDADE_PROGRAMA                                     as modalidade,
    NM_GRAU_PROGRAMA                                           as grau,
    NM_GRAU_PROGRAMA like '%MESTRADO%'                         as oferta_mestrado,
    NM_GRAU_PROGRAMA like '%DOUTORADO%'                        as oferta_doutorado,

    try_cast(CD_CONCEITO_PROGRAMA as integer)                  as conceito,
    CD_CONCEITO_PROGRAMA = 'A'                                 as em_implantacao,

    coalesce(AN_INICIO_PROGRAMA, ANO_INICIO_PROGRAMA)::integer as ano_inicio,
    IN_REDE = 'SIM'                                            as em_rede,
    DS_SITUACAO_PROGRAMA                                       as situacao,
    strptime(DT_SITUACAO_PROGRAMA, '%d%b%Y:%H:%M:%S')::date    as dt_situacao,

    _resource_id                                               as _resource_id
from {{ source('bronze', 'programas') }}
