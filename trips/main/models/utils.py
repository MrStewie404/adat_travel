import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string

from main.utils.utils import get_transliterated_filename, make_thumbnail

price_max_digits = 7 + 2
price_decimal_places = 2


def create_price_field(verbose_name, name=None, **kwargs):
    max_digits = kwargs.pop('max_digits', price_max_digits)
    decimal_places = kwargs.pop('decimal_places', price_decimal_places)
    validators = kwargs.pop('validators', [MinValueValidator(0)])
    return models.DecimalField(verbose_name, name, max_digits=max_digits, decimal_places=decimal_places,
                               validators=validators, **kwargs)


def get_unique_token(model_class, field_name, length=12, max_iterations=100):
    """В текущей реализации просто возвращает случайную строку заданной длины."""
    queryset = model_class.objects
    filter_kwargs = {}
    token = None
    i = 1
    finish = False
    while not finish:
        token = get_random_string(length)
        filter_kwargs[field_name] = token
        finish = not queryset.filter(**filter_kwargs).exists() or i > max_iterations
        i += 1
    if i > max_iterations:
        logging.error(f"Failed to generate random unique string for {model_class}.{field_name}")
        return None
    return token


def file_upload_path(instance, filename):
    """Выдаёт путь к медиафайлу на диске. У каждого агентства своя папка. Агентство извлекается из поля agency."""
    from main.models.agency.agency import Agency
    agency = instance.agency
    agency_name = Agency.get_valid_filename(agency, prepend_pk=True)
    class_name = get_transliterated_filename(type(instance).__name__).lower()
    safe_filename = get_transliterated_filename(filename)
    return f"uploads/{agency_name}/{class_name}/{safe_filename}"


def replace_image_with_thumbnail(model, field_name, max_width=640, max_height=480, format='JPEG'):
    with BytesIO() as f:
        image_field = getattr(model, field_name)
        make_thumbnail(image_field.file, f, max_width=max_width, max_height=max_height, format=format)
        f.seek(0)
        image_file = ImageFile(ContentFile(f.read(), image_field.name))
        setattr(model, field_name, image_file)
