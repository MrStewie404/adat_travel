from django import template

register = template.Library()


@register.filter
def at(collection, index):
    if not collection:
        return None  # Сюда подпадает и None, и пустая строка, и пустая коллекция
    return collection[index]
