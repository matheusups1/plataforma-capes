select indicador_id, ano, recorte_tipo, recorte_valor, valor
from {{ ref('mart_indicador_valor') }}
where unidade = 'percentual' and (valor < 0 or valor > 100)
