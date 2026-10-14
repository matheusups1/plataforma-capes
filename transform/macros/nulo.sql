{#- Texto vazio e o marcador 'NA' do portal viram NULL. -#}
{% macro nulo(coluna) -%}
nullif(nullif(trim({{ coluna }}), ''), 'NA')
{%- endmacro %}
