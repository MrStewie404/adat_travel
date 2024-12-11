from typing import Union

from django.forms import TextInput, Textarea, NumberInput, DateInput, SplitDateTimeWidget, Select, SelectMultiple, \
    CheckboxInput, EmailInput, URLInput, TimeInput


def get_size_style_setter(attr_name, value: Union[str, int]):
    if value is None:
        return ''
    value_str = f"{value}px" if isinstance(value, int) else value
    return f"{attr_name}:{value_str};"


def text_input(placeholder, height: Union[str, int] = None, maxlength=None):
    attrs = {
        'class': 'form-control',
        'placeholder': placeholder,
    }
    if maxlength:
        attrs['maxlength'] = str(maxlength)

    if height:
        attrs['style'] = get_size_style_setter('height', height)
    return TextInput(attrs)


def search_text_input():
    attrs = {
        'class': 'form-control rn-search-input',
        'placeholder': 'Введите строку для поиска',
    }
    return TextInput(attrs)


def textarea(placeholder, rows=None):
    attrs = {
        'class': 'form-control',
        'placeholder': placeholder,
    }
    if rows:
        attrs['rows'] = rows
    return Textarea(attrs=attrs)


def number_input(placeholder, css_class='form-control', **kwargs):
    return NumberInput(attrs={
        'class': css_class,
        'placeholder': placeholder,
        **kwargs,
    })


def money_input(placeholder, css_class='form-control', **kwargs):
    attrs = {
        'class': css_class,
        'placeholder': placeholder,
        'inputmode': 'numeric',
        'pattern': money_pattern(),
        'title': 'Cумма в рублях (разрешается использовать цифры и точку для разделения рублей и копеек)',
    }
    attrs.update(**kwargs)
    return TextInput(attrs=attrs)


def money_pattern():
    return r"[0-9]{1-7}(.[0-9]{0,2)?"


def date_pattern():
    return r"(0?[1-9]|1[0-9]|2[0-9]|3[01])\.(0?[1-9]|1[012])\.(19|20)[0-9]{2}"


def date_input(placeholder='Дата', css_class='form-control-sm bootstrap-date-picker2 form-control',
               height: Union[str, int] = None,
               width: Union[str, int] = None,):
    attrs = {
        'class': css_class,
        'type': 'text',
        'placeholder': placeholder,
        'pattern': date_pattern(),
        'title': 'Дата в формате ДД.ММ.ГГГГ',
        'autocomplete': 'off',  # Отключаем автозаполнение, перекрывающее календарь
    }

    if height or width:
        attrs['style'] = get_size_style_setter('width', width) + \
                         get_size_style_setter('height', height)

    # Чтобы всё работало, формат ДД.ММ.ГГГГ должен быть также задан для datetimepicker-а в javascript.
    return DateInput(format='%d.%m.%Y', attrs=attrs)


def time_input(css_class='form-control-sm', format='%H:%M', height: Union[str, int] = 35):
    attrs = {
        'class': css_class,
        'type': 'time',
        'autocomplete': 'off',  # Отключаем автозаполнение
        'style': get_size_style_setter('height', height),
    }
    return TimeInput(format=format, attrs=attrs)


def multi_date_input(placeholder='Выберите даты'):
    attrs = {
        'class': 'form-control date-picker-multiselect',
        'type': 'text',
        'placeholder': placeholder,
        'title': 'Даты через запятую в формате ДД.ММ.ГГГГ',
        'autocomplete': 'off',  # Отключаем автозаполнение, перекрывающее календарь
    }
    return TextInput(attrs=attrs)


def split_date_time_widget():
    return SplitDateTimeWidget(
        date_format='%d.%m.%Y',
        date_attrs={
            'class': 'form-control-sm bootstrap-date-picker2',
            'type': 'text',
            'placeholder': 'Дата',
            'pattern': date_pattern(),
            'title': 'Дата в формате ДД.ММ.ГГГГ',
            'autocomplete': 'off',  # Отключаем автозаполнение, перекрывающее календарь
        },
        time_attrs={
            'class': 'form-control-sm timepicker m-l-10',
            'type': 'time',
            'placeholder': 'Время',
        },
    )


def select(submit=False, width: Union[str, int] = None, height: Union[str, int] = None):
    attrs = {
        'class': 'form-control',
    }
    if submit:
        attrs['onChange'] = "form.submit();"
    attrs['style'] = get_size_style_setter('width', width) + \
                     get_size_style_setter('height', height) or 'height: auto;'
    return Select(attrs=attrs)


def rich_select(placeholder, css_class='js-select2', multiple=False, submit=False,
                width: Union[str, int] = '100%', height: Union[str, int] = None):
    attrs = {
        'class': css_class,
        'placeholder': placeholder,
        'style': f"{get_size_style_setter('width', width)}{get_size_style_setter('height', height)}",
    }
    if submit:
        attrs['onChange'] = "form.submit();"
    return SelectMultiple(attrs=attrs) if multiple else Select(attrs=attrs)


def checkbox(css_class='custom-checkbox', submit=False):
    attrs = {
        'class': css_class,
    }
    if submit:
        attrs['onChange'] = "form.submit();"
    return CheckboxInput(attrs=attrs)


def email_input(placeholder='E-Mail'):
    return EmailInput(attrs={
        'class': 'form-control',
        'placeholder': placeholder,
    })


def url_input(placeholder):
    return URLInput(attrs={
        'class': 'form-control',
        'placeholder': placeholder,
    })


def color_input(placeholder, css_class, width: Union[str, int] = 100, height: Union[str, int] = None):
    return rich_select(placeholder, css_class=css_class, width=width, height=height)


def color_choices():
    # Цвета взяты из gitlab (+ несколько добавлено)
    return [
        ('#009966', 'Green-cyan'),
        ('#8FBC8F', 'Dark sea green'),
        ('#3CB371', 'Medium sea green'),
        ('#00B140', 'Green screen'),
        ('#00FF00', 'Green'),
        ('#013220', 'Dark green'),
        ('#6699CC', 'Blue-gray'),
        ('#0000FF', 'Blue'),
        ('#0096FF', 'Bright blue'),
        ('#E6E6FA', 'Lavender'),
        ('#9400D3', 'Dark violet'),
        ('#330066', 'Deep violet'),
        ('#808080', 'Gray'),
        ('#36454F', 'Charcoal gray'),
        ('#F7E7cE', 'Champagne'),
        ('#C21E56', 'Rose red'),
        ('#CC338B', 'Magenta-pink'),
        ('#DC143C', 'Crimson'),
        ('#FF0000', 'Red'),
        ('#CD5B45', 'Dark coral'),
        ('#EEE600', 'Titanium yellow'),
        ('#ED9121', 'Carrot orange'),
        ('#F57C00', 'Orange'),
        ('#C39953', 'Aztec gold'),
    ]
