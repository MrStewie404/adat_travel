from typing import SupportsRound
import re

from django import template

register = template.Library()


@register.filter
def currency(value, precision=2):
    # TODO: написать тест
    if value is None or not issubclass(type(value), SupportsRound):
        return ''
    # Нужно обязательно округлять, чтобы не "пролезло" какое-нибудь кривое значение.
    # Округляю отдельной функцией, т.к. не нашёл, как добавить округление к спецификатору "n"
    # (он используется для печати разделителя групп разрядов с учётом текущей локали).
    # P.S. Текущая локаль у нас задаётся в settings-ах.
    rounded = round(value, precision)
    return f"{rounded:n}"


@register.filter()
def phonenumber(phone_number):
    new_phone = re.sub(r'\D', '', phone_number)  # убираем все нецифровые символы
    if len(new_phone) == 11:
        if new_phone.startswith("8") and "+" not in phone_number:
            new_phone = f"7{new_phone[1:]}"
        new_phone = f'+{new_phone[0:1]} ({new_phone[1:4]}) {new_phone[4:7]}-{new_phone[7:9]}-{new_phone[9:]}'  # форматируем номер в нужный вид
        return new_phone

    return phone_number

