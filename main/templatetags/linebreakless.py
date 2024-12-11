import re

import six
from django import template
from django.template.base import Node
from django.utils.functional import keep_lazy

register = template.Library()


@register.tag
def linebreakless(parser, token):
    """
    Удаляет переносы строк (вместе с окружающими пробелами) из текстового содержимого тега.
    Идея взята отсюда: https://stackoverflow.com/a/37541270
    """
    nodelist = parser.parse(('endlinebreakless',))
    parser.delete_first_token()
    return LinebreaklessNode(nodelist)


class LinebreaklessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        strip_line_breaks = keep_lazy(six.text_type)(lambda x: re.sub(r"\s*\n\s*", '', x))
        return strip_line_breaks(self.nodelist.render(context).strip())
