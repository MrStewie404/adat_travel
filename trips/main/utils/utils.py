import os
import re
import urllib.parse
from calendar import monthrange
from datetime import timedelta
from decimal import Decimal

import idna
import magic
from PIL import Image
from django.core.exceptions import SuspiciousFileOperation
from django.template import defaultfilters
from django.template.defaultfilters import rjust
from django.utils import numberformat
from django.utils.text import get_valid_filename, Truncator


def format_money(amount_sum, show_r_sign=True, digit_places=0):
    num_str = numberformat.format(amount_sum, decimal_sep=',', decimal_pos=2, grouping=3, thousand_sep=' ',
                                  force_grouping=True)
    num_str = rjust(num_str, digit_places)
    if show_r_sign:
        return num_str + ' ₽'
    return num_str


def transliterate(text):
    # Стандарт транслитерации для загранпаспорта 2020 (см. https://www.icao.int/publications/Documents/9303_p3_cons_ru.pdf)
    icao_9303_table = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'i',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ъ': 'ie',
        'ы': 'y',
        'ь': '',
        'э': 'e',
        'ю': 'iu',
        'я': 'ia',
    }
    full_table = {**icao_9303_table, **{k.upper(): v.capitalize() for k, v in icao_9303_table.items()}}
    return text.translate(text.maketrans(full_table))


def get_transliterated_filename(text):
    """Транслитерирует строку, преобразует её в "чистое" имя файла с помощью get_valid_filename."""
    return get_valid_filename(transliterate(text))


def get_valid_filename_light(file_name, valid_chars=r'-\w(). '):
    """
    Менее агрессивный аналог джанговского метода get_valid_filename, оставляет пробелы
    и некоторые другие неопасные для файловой системы символы.
    Может понадобиться, например, при кешировании пользовательских имён файлов, чтобы при скачивании
    имя файла по возможности совпадало с именем загруженного файла.
    """
    # TODO: написать тесты
    s = re.sub(rf"(?u)[^{valid_chars}]", '', file_name.strip())
    if s in {'', '.', '..'}:
        raise SuspiciousFileOperation("Не удалось получить корректное имя файла из строки '%s'" % file_name)
    return s


def get_month_name(month_no):
    months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return months[month_no - 1]


def django_date_str(date, str_format):
    return defaultfilters.date(date, str_format)


def get_unique_name(name, existing_names, allow_use_initial=True):
    ind = 1
    res = name if allow_use_initial else f"{name} ({ind})"
    while res in existing_names:
        ind += 1
        res = f"{name} ({ind})"
    return res


def int_or_default(string, default=None):
    try:
        return int(string)
    except TypeError:
        return default
    except ValueError:
        return default
    return default


def decimal_or_default(string, default=None):
    try:
        return Decimal(string)
    except TypeError:
        return default
    except ValueError:
        return default
    return default


def str_to_bool(string):
    if not string:
        return False
    return string.lower() == 'true'


def hours_to_days(hours):
    return (hours // 24) + (hours % 24 > 0)


def is_image_extension(file_name):
    return file_name.lower().endswith(('.jpg', '.jpeg', '.bmp', '.png', '.tiff', '.ico'))


def is_valid_image(path, check_extension=True, check_loadable=True, max_width=3840, max_height=2160):
    """
    Проверка, что файл является корректным изображением.
    Проверяем расширение, тип картинки из заголовка, открывается ли картинка библиотекой Pillow
    и проходит ли её проверки. Дополнительно проверяем размеры (по умолчанию ограничения более жёсткие,
    чем в библиотеке Pillow, где проверяется уязвимость типа "Decompression Bomb").
    """
    # TODO: написать тесты
    if check_extension and not is_image_extension(path):
        return False
    if not os.path.isfile(path):
        return False

    allowed_formats = ('jpeg', 'bmp', 'png', 'tiff', 'ico')

    # if imghdr.what(path) not in allowed_formats:
    #     return False

    try:
        with Image.open(path) as im:
            if im.format.lower() not in allowed_formats:
                return False
            if max_width and im.width > max_width:
                return False
            if max_height and im.height > max_height:
                return False
            # verify следует вызывать сразу после open, до обращения к данным
            # (при этом выше мы обращаемся к полям format, width и height - они уже должны быть заполнены после open)
            im.verify()  # После вызова verify() нужно заново открывать картинку
        if check_loadable:
            # Для верности попробуем загрузить картинку
            with Image.open(path) as im:
                im.load()
    except Exception:  # Pillow может выкинуть что угодно
        return False

    return True


def is_valid_pdf(path, check_extension=True):
    """
    Проверка, что файл является корректным PDF.
    Проверяем расширение и тип файла из заголовка.
    """
    if check_extension and not path.lower().endswith('.pdf'):
        return False
    if not os.path.isfile(path):
        return False
    if magic.from_file(path, mime=True) != "application/pdf":
        return False

    return True


def make_thumbnail(path, output_stream, max_width, max_height, format=None):
    with Image.open(path) as im:
        if im.width > max_width or im.height > max_height:
            output_size = (max_width, max_height)
            im.thumbnail(output_size)
        if format:
            im.convert('RGB')
        im.save(output_stream, format=format)


def date_birth_on_or_after(date_birth, start_date):
    """Возвращает ближайший день рождения, начиная с указанной даты."""
    if not date_birth or not start_date:
        raise ValueError('Отсутствует значение даты рождения или начальной даты.')
    result = date_birth
    if (date_birth.month, date_birth.day) == (2, 29) and (start_date.month, start_date.day) == (3, 1):
        # Для родившихся 29 февраля дата рождения может считаться как 28 февраля, так и 1 марта
        result = result + timedelta(days=1)
    result = replace_year(result, start_date.year)
    if result < start_date:
        result = replace_year(date_birth, start_date.year + 1)
    return result


def replace_year(date, new_year):
    new_day = min(date.day, monthrange(new_year, date.month)[1])  # Нужно скорректировать день на случай 29 февраля
    return date.replace(year=new_year, day=new_day)


def decode_domain_name(url):
    """
    Возвращает новый url с декодированным доменным именем, которое может содержать символы Юникода
    (по умолчанию Джанго всегда кодирует url, поэтому кириллица заменяется набором латинских символов -
    ссылка получается непрезентабельная).
    См. также https://docs.djangoproject.com/en/4.0/ref/unicode/#uri-and-iri-handling
    """
    idn_prefix = 'xn--'
    if idn_prefix not in url:
        return url
    parts = urllib.parse.urlsplit(url)
    domain_name = parts.netloc
    if idn_prefix not in domain_name:
        return url
    parts = parts._replace(netloc=idna.decode(domain_name))
    return urllib.parse.urlunsplit(parts)


def truncate_str(text, length, truncate=None):
    return Truncator(text).chars(length, truncate=truncate)


def truncate_str_custom(text, length):
    return truncate_str(text, length, truncate='(…)')


# def max_date_of(date1, date2):
#     return date1 if date1 > date2 else date2
#
#
# def min_date_of(date1, date2):
#     return date1 if date1 < date2 else date2
