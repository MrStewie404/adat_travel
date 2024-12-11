from django.core.exceptions import ImproperlyConfigured
from django.db.models import SlugField

from main.models.utils import get_unique_token


class RandomSlugField(SlugField):
    """
    Поле со случайным и уникальным значением. Значение генерируется автоматически при сохранении модели.
    Можно использовать для скрытия pk во внешних url.
    Внимание: при добавлении в модель поле не заполняется автоматически в уже существующих записях,
    его можно заполнить только в отдельной миграции.
    """
    default_length = 12
    description = "Random slug string, unique per model (length = %(length)s)"

    def __init__(self, *args, length=default_length, blank=True, null=True, unique=True, editable=False, **kwargs):
        self.length = length
        max_length = kwargs.pop('max_length', length)
        super().__init__(*args, max_length=max_length, blank=blank, null=null, unique=unique, editable=editable,
                         **kwargs)
        if self.length > self.max_length:
            raise ImproperlyConfigured("Length must be less or equal than max_length")

    def get_unique_slug(self, model_instance):
        return get_unique_token(model_instance.__class__, self.attname, length=self.length)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if not value:
            value = self.get_unique_slug(model_instance)
            setattr(model_instance, self.attname, value)
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.max_length == self.length:
            del kwargs['max_length']
        if self.length != self.default_length:
            kwargs['length'] = self.length
        return name, path, args, kwargs
