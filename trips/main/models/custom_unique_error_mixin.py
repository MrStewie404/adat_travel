from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models


class CustomUniqueErrorMixin(models.Model):
    """
    Сообщение об ошибке для unique together constraints (т.е. ограничений уровня модели)
    захардкожено в методе Model.unique_error_message.
    Этот mixin позволяет легко подменить дефолтное сообщение об ошибке.
    P.S. Получается немного странная конструкция: Mixin представляет собой абстрактную модель,
    но при этом, вроде как, без ошибок подмешивается к обычным моделям. Раз работает, пусть остаётся так.
    """

    def get_unique_together_error_message(self):
        return None

    def unique_error_message(self, model_class, unique_check):
        e = super().unique_error_message(model_class, unique_check)

        # A unique field
        if len(unique_check) == 1:  # unique_together
            return e

        msg = self.get_unique_together_error_message()
        if not msg:
            raise ImproperlyConfigured(
                "%(cls)s is missing a unique together message. "
                "Please override %(cls)s.get_unique_together_error_message()." % {
                    'cls': self.__class__.__name__
                }
            )
        return ValidationError(msg, code=e.code, params=e.params)

    class Meta:
        abstract = True
