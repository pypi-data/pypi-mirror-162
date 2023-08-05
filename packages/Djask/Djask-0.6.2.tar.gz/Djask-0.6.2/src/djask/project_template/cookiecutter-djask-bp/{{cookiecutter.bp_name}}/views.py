{%- if cookiecutter.type == 'api' -%}
{%- set class_name = 'APIBlueprint' -%}
{%- else -%}
{%- set class_name = 'Blueprint' -%}
{%- endif -%}
{%- set bp_name = cookiecutter.bp_name -%}
from djask import {{ class_name }}

{{ '{0}_bp = {1}("{0}", __name__, url_prefix="/{0}")'.format(bp_name, class_name) }}

@{{ bp_name }}_bp.route("")
def bp_index():
    return "Hello World!"
