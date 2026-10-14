-- Um registro por curso (mestrado/doutorado) × ano-base. Todo curso pertence a um programa do mesmo ano.
select
    _ano::integer                                       as ano,
    CD_CURSO_PPG                                        as cd_curso,
    CD_PROGRAMA_IES                                     as cd_programa,
    CD_ENTIDADE_CAPES                                   as cd_ies,
    CD_AREA_AVALIACAO::integer                          as cd_area_avaliacao,
    NM_CURSO                                            as nm_curso,
    NM_GRAU_CURSO                                       as grau,
    NM_GRAU_CURSO like 'DOUTORADO%'                     as eh_doutorado,
    NM_GRAU_CURSO like '%PROFISSIONAL'                  as eh_profissional,
    -- '-1' aparece em 69 registros sem conceito atribuído; tratado como NULL
    case when CD_CONCEITO_CURSO in ('1','2','3','4','5','6','7')
         then CD_CONCEITO_CURSO::integer end            as conceito,
    CD_CONCEITO_CURSO = 'A'                             as em_implantacao,
    try_cast(AN_INICIO_PREVISTO as integer)             as ano_inicio,
    DS_SITUACAO_CURSO                                   as situacao,
    try_strptime(DT_SITUACAO_CURSO, '%d%b%Y:%H:%M:%S')::date as dt_situacao,
    NM_REGIAO                                           as regiao,
    SG_UF_PROGRAMA                                      as uf,
    DS_DEPENDENCIA_ADMINISTRATIVA                       as dependencia_adm,
    CS_STATUS_JURIDICO                                  as status_juridico
from {{ source('bronze', 'cursos') }}
