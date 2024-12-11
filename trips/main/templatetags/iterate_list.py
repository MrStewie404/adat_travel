from django import template


register = template.Library()


@register.simple_tag()
def iterate_list(list, i):
    return list[i]
