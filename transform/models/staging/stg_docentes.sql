-- Vínculos docente × programa × ano-base.
-- PRIVACIDADE: nome e documento (NM_DOCENTE, NR_DOCUMENTO_DOCENTE) são descartados aqui;
-- só o identificador pseudônimo ID_PESSOA segue, para contar pessoas distintas.
-- QUALIDADE: 2017–2019 trazem 3.194 linhas duplicadas na fonte (mesma pessoa/programa/ano,
-- demais campos idênticos); mantemos uma.
with fonte as (
    select *
    from {{ source('bronze', 'docentes') }}
    qualify row_number() over (partition by ID_PESSOA, CD_PROGRAMA_IES, _ano order by _resource_id) = 1
)
select
    _ano::integer                                         as ano,
    ID_PESSOA                                             as id_pessoa,
    CD_PROGRAMA_IES                                       as cd_programa,
    CD_ENTIDADE_CAPES                                     as cd_ies,
    CD_AREA_AVALIACAO::integer                            as cd_area_avaliacao,
    NM_MODALIDADE_PROGRAMA                                as modalidade,
    NM_REGIAO                                             as regiao,
    SG_UF_PROGRAMA                                        as uf,
    DS_DEPENDENCIA_ADMINISTRATIVA                         as dependencia_adm,

    DS_CATEGORIA_DOCENTE                                  as categoria,
    {{ nulo('DS_TIPO_VINCULO_DOCENTE_IES') }}             as tipo_vinculo,
    {{ nulo('DS_REGIME_TRABALHO') }}                      as regime_trabalho,
    {{ nulo('CD_CAT_BOLSA_PRODUTIVIDADE') }}              as bolsa_produtividade_cnpq,

    try_cast(AN_NASCIMENTO_DOCENTE as integer)            as ano_nascimento,
    {{ nulo('DS_FAIXA_ETARIA') }}                         as faixa_etaria,
    DS_TIPO_NACIONALIDADE_DOCENTE = 'ESTRANGEIRO'         as estrangeiro,
    {{ nulo('NM_PAIS_NACIONALIDADE_DOCENTE') }}           as pais_nacionalidade,

    IN_DOUTOR = 'S'                                       as doutor,
    try_cast(AN_TITULACAO as integer)                     as ano_titulacao,
    replace({{ nulo('NM_GRAU_TITULACAO') }}, 'DOUTORDO', 'DOUTORADO') as grau_titulacao,
    {{ nulo('NM_AREA_BASICA_TITULACAO') }}                as area_titulacao,
    nullif({{ nulo('SG_IES_TITULACAO') }}, 'NI')          as sg_ies_titulacao,
    {{ nulo('NM_PAIS_IES_TITULACAO') }}                   as pais_titulacao,
    {{ nulo('NM_PAIS_IES_TITULACAO') }} <> 'BRASIL'        as titulado_exterior
from fonte
