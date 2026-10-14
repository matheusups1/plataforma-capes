-- Catálogo de teses e dissertações: um registro por trabalho defendido.
-- PRIVACIDADE: nomes de discente e orientador são descartados (ids pseudônimos mantidos).
-- Resumo/abstract ficam só no bronze (volume); palavras-chave seguem para análise de temas.
-- CD_ENTIDADE_CAPES só existe a partir de 2017: a IES vem do programa (ver fct_teses).
select
    _ano::integer                                          as ano,
    ID_ADD_PRODUCAO_INTELECTUAL                            as id_trabalho,
    CD_PROGRAMA                                            as cd_programa,
    ID_PESSOA_DISCENTE                                     as id_pessoa_discente,
    ID_PESSOA_ORIENTADOR                                   as id_pessoa_orientador,
    NM_PRODUCAO                                            as titulo,
    NM_GRAU_ACADEMICO                                      as nivel,
    NM_GRAU_ACADEMICO like 'DOUTORADO%'                    as eh_doutorado,
    {{ data_capes('DT_TITULACAO') }}                       as dt_titulacao,
    {{ data_capes('DT_MATRICULA') }}                       as dt_matricula,
    try_cast(NR_PAGINAS as integer)                        as paginas,
    {{ nulo('NM_IDIOMA') }}                                as idioma,
    {{ nulo('DS_PALAVRA_CHAVE') }}                         as palavras_chave,
    {{ nulo('NM_AREA_CONCENTRACAO') }}                     as area_concentracao,
    {{ nulo('NM_LINHA_PESQUISA') }}                        as linha_pesquisa,
    nullif({{ nulo('NM_EXPECTATIVA_ATUACAO') }}, 'NÃO INFORMADO') as expectativa_atuacao,
    nullif({{ nulo('NM_CATEGORIA_DOCENTE') }}, 'NÃO INFORMADO')   as categoria_orientador,
    IN_ORIENT_PARTICIPOU_BANCA = '1'                       as orientador_na_banca,
    {{ nulo('DS_URL_TEXTO_COMPLETO') }} is not null        as tem_texto_completo,
    NM_GRANDE_AREA_CONHECIMENTO                            as grande_area,
    NM_AREA_CONHECIMENTO                                   as area_conhecimento
from {{ source('bronze', 'teses') }}
