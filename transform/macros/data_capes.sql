{#-
  Datas do portal vêm em três formatos, às vezes misturados no mesmo arquivo:
    01MAR2017:00:00:00  (18 chars)   04APR13:00:00:00  (16 chars)   17/12/2014 00:00:00
  O formato é escolhido pelo tamanho: aplicar %Y a '04APR13' "funciona" e devolve o ano 13 d.C.
-#}
{% macro data_capes(coluna) -%}
case
    when {{ coluna }} like '__/__/____%'   then try_strptime({{ coluna }}, '%d/%m/%Y %H:%M:%S')
    when length({{ coluna }}) = 18         then try_strptime({{ coluna }}, '%d%b%Y:%H:%M:%S')
    when length({{ coluna }}) = 16         then try_strptime({{ coluna }}, '%d%b%y:%H:%M:%S')
end::date
{%- endmacro %}
