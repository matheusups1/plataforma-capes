-- Cada capital do seed precisa casar com algum programa: pega erros de grafia no seed
-- (que fariam programas da capital serem contados como "fora das capitais").
select c.uf, c.capital
from {{ ref('capitais') }} c
where not exists (
    select 1 from {{ ref('fct_programa_ano') }} f
    where f.uf = c.uf and f.em_capital
)
