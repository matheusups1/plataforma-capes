{#- Todo registro (cd_programa, ano) do modelo precisa existir em programas naquele ano. -#}
{% test programa_existe_no_ano(model) %}
select f.cd_programa, f.ano
from {{ model }} f
anti join {{ ref('int_programa_recortes') }} p using (cd_programa, ano)
{% endtest %}
