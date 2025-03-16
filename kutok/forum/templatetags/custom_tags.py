from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def query_update(request, **kwargs):
    """
    Обновляет query-параметры в URL.
    Если передан параметр remove=True, удаляет указанный ключ из query-параметров.
    """
    params = request.GET.copy()
    remove = kwargs.pop('remove', False)
    
    for key, value in kwargs.items():
        if remove:
            params.pop(key, None)
        else:
            params[key] = value
    
    return urlencode(params)