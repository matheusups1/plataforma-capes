{{ config(materialized='table') }}
-- Um registro por trabalho × palavra-chave. O campo da fonte separa termos por ';' (73%) ou,
-- na falta dele, por ','; pontos finais são removidos. `chave` agrupa variações de caixa,
-- acento e espaço ("Educação", "EDUCACAO"); `forma` guarda o termo como foi escrito.
with fonte as (
    select id_trabalho, ano, grande_area, palavras_chave as p
    from {{ ref('stg_teses') }}
    where palavras_chave is not null
),
termos as (
    select id_trabalho, ano, grande_area,
           unnest(string_split(p, case when p like '%;%' then ';' else ',' end)) as termo
    from fonte
),
limpos as (
    select id_trabalho, ano, grande_area,
           regexp_replace(trim(regexp_replace(trim(termo), '[.]+$', '')), '\s+', ' ', 'g') as forma
    from termos
)
select distinct
    id_trabalho,
    ano,
    grande_area,
    lower(forma)                 as forma,
    lower(strip_accents(forma))  as chave
from limpos
where length(forma) between 2 and 80
