from django.core.validators import RegexValidator
from django.utils.regex_helper import _lazy_re_compile

social_network_account_validator = RegexValidator(
    regex=_lazy_re_compile(r"^[a-zA-Z0-9_.@]*$"),
    message="Допустимы латинские буквы, цифры и специальные символы (подчёркивание, точка и @).",
    code='account_check_fail',
)


def validate_social_network_account(value):
    social_network_account_validator(value)
