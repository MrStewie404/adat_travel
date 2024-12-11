from django.db import models
from django.utils import timezone

from main.models.clients.abstract_person import AbstractPerson


class Person(AbstractPerson):
    """Персона (базовый класс для клиентов, работников и т.д.)."""
    created_by = models.ForeignKey('AgencyEmployee', on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_persons')
    created_at = models.DateTimeField('Дата создания', default=timezone.now, blank=True, null=True)
    modified_by = models.ForeignKey('AgencyEmployee', on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='modified_persons')
    modified_at = models.DateTimeField('Дата изменения', default=timezone.now, blank=True, null=True)

    class Meta:
        verbose_name = 'Персональные данные'
        verbose_name_plural = 'Персональные данные'
