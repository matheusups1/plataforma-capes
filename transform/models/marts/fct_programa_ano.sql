-- Grão: programa × ano-base. Base para indicadores dos módulos 01 e 02.
select
    p.ano,
    cd_programa,
    cd_ies,
    cd_area_avaliacao,
    regiao,
    p.uf,
    municipio,
    c.capital is not null as em_capital,
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
from {{ ref('stg_programas') }} p
-- comparação sem acento: a grafia do município na fonte nem sempre traz acentos
left join {{ ref('capitais') }} c
    on c.uf = p.uf and strip_accents(c.capital) = strip_accents(p.municipio)
