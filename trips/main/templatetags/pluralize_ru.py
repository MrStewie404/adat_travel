from django import template

register = template.Library()


@register.filter(is_safe=False)
def pluralize_ru(value, forms):
    """
    Функция аналогична django.template.defaultfilters.pluralize,
    только учитывает третью форму согласования числительных с существительными в русском языке.
    Переменная forms должна содержать три формы существительного (или только его окончания) через запятую.

    Примеры:
    * Если value = 0, то pluralize_ru(value, "день,дня,дней") вернёт "дней".
    * Если value = 1, то pluralize_ru(value, "день,дня,дней") вернёт "день".
    * Если value = 2, то pluralize_ru(value, "день,дня,дней") вернёт "дня".
    * Если value = 5, то pluralize_ru(value, "день,дня,дней") вернёт "дней".
    """
    forms_list = forms.split(',')
    if len(forms_list) != 3:
        return ''
    singular_form, two_three_four_form, plural_form = forms_list[:3]

    try:
        v_int = int(value)
    except ValueError:  # Строка не может быть преобразована к целому числу.
        return ''
    except TypeError:  # Значение не является строкой или числом.
        return ''

    ones = v_int % 10
    tens = (v_int // 10) % 10
    if tens == 1 or ones == 0 or ones >= 5:
        result = plural_form
    elif ones == 1:
        result = singular_form
    else:
        result = two_three_four_form
    return result
