-- Grão: programa × ano-base. Base para indicadores dos módulos 01 e 02.
select
    ano,
    cd_programa,
    cd_ies,
    cd_area_avaliacao,
    regiao,
    uf,
    status_juridico,
    dependencia_adm,
    modalidade,
    grau,
    oferta_mestrado,
    oferta_doutorado,
    conceito,
    em_implantacao,
    ano_inicio,
    em_rede,
    situacao
from {{ ref('stg_programas') }}
