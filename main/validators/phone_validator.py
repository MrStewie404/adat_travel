import logging

import phonenumbers
from django.core.exceptions import ValidationError


message = "Неверный формат номера телефона или код оператора."


def clean_and_validate_phone(value):
    logger = logging.getLogger(__name__)
    try:
        if value:
            try:
                parsed_number = phonenumbers.parse(value, region='RU')
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValidationError(message)
            except phonenumbers.NumberParseException:
                raise ValidationError(message)
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        return value
    except Exception as e:
        logger.info(f"!!! Wrong phone number {value}")
        raise


def replace_russian_8(s):
    s = s.lstrip()  # удаляем ведущие пробелы
    if s.startswith('8'):
        s = '+7' + s[1:]
    elif s.startswith('+8'):
        s = '+7' + s[2:]
    return s
