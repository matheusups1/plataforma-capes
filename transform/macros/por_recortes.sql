{#-
  Calcula um indicador para o Brasil e para cada recorte, por ano, em formato longo:
    indicador_id, ano, recorte_tipo, recorte_valor, valor, numerador, denominador

  `relacao` precisa ter as colunas de int_programa_recortes (ano, regiao, uf, ...).
  `valor`, `numerador` e `denominador` são expressões de agregação SQL, recalculadas em
  cada recorte (por isso razões são corretas: soma/soma, nunca média de médias).
-#}
{% macro recortes() %}
    {{ return(['regiao', 'uf', 'grande_area', 'area_avaliacao', 'modalidade', 'dependencia_adm', 'conceito']) }}
{% endmacro %}

{% macro por_recortes(indicador_id, relacao, valor, numerador='null', denominador='null') %}
{%- set lista = recortes() %}
select
    '{{ indicador_id }}'                as indicador_id,
    ano,
    case
    {%- for r in lista %}
        when grouping({{ r }}) = 0 then '{{ r }}'
    {%- endfor %}
        else 'brasil'
    end                                 as recorte_tipo,
    case
    {%- for r in lista %}
        when grouping({{ r }}) = 0 then {{ r }}::varchar
    {%- endfor %}
        else 'BRASIL'
    end                                 as recorte_valor,
    ({{ valor }})::double               as valor,
    ({{ numerador }})::double           as numerador,
    ({{ denominador }})::double         as denominador
from {{ relacao }}
group by grouping sets (
    (ano)
    {%- for r in lista %},
    (ano, {{ r }})
    {%- endfor %}
)
{% endmacro %}

{#- Razão percentual com numerador/denominador preservados para auditoria. -#}
{% macro pct_por_recortes(indicador_id, relacao, numerador, denominador) %}
{{ por_recortes(indicador_id, relacao,
    valor='100.0 * (' ~ numerador ~ ') / nullif(' ~ denominador ~ ', 0)',
    numerador=numerador, denominador=denominador) }}
{% endmacro %}

{#- Razão simples (ex. discentes por docente, meses médios). -#}
{% macro razao_por_recortes(indicador_id, relacao, numerador, denominador) %}
{{ por_recortes(indicador_id, relacao,
    valor='(' ~ numerador ~ ')::double / nullif(' ~ denominador ~ ', 0)',
    numerador=numerador, denominador=denominador) }}
{% endmacro %}
