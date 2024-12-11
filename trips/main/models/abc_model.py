import abc

from django.db import models


class ABCModelMeta(abc.ABCMeta, type(models.Model)):
    """Метакласс для моделей с абстрактными методами."""
    pass


class ABCModel(models.Model, metaclass=ABCModelMeta):
    """Базовый класс для моделей с абстрактными методами.
    Добавляет проверку, что все абстрактные методы определены в моделях-наследниках,
    если же это не так - вылетит исключение при попытке создания экземпляра наследника.
    """

    class Meta:
        abstract = True
