from django.conf import settings
from django.db import models

from main.models.clients.person import Person


class AgencyEmployee(Person):
    """Сотрудник турфирмы."""

    class RoleEnum(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        MANAGER = 'MANAGER', 'Менеджер'
        SERVICE_GUIDE = 'SERVICE_GUIDE', 'Сервисный гид'
        TOUR_PLANNER = 'TOUR_PLANNER', 'Разработчик туров'

        __empty__ = '(Выберите роль)'

    person_ptr = models.OneToOneField(Person, on_delete=models.CASCADE, parent_link=True,
                                      related_name='agency_employee')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=False,
                                blank=True, null=True, related_name='agency_employee')
    role = models.CharField(
        'Роль',
        max_length=32,
        choices=RoleEnum.choices,
        blank=True,
    )

    def __str__(self):
        role_str = self.RoleEnum(self.role).label if self.role else 'Неизвестная роль'
        return f"{self.full_name()} ({role_str})"

    def try_get_avatar(self):
        return getattr(self, 'avatar', None)

    @staticmethod
    def get_agency_employee(user):
        # Работает правильно, даже если user is None
        return getattr(user, 'agency_employee', None)

    @staticmethod
    def get_agency(user):
        employee = AgencyEmployee.get_agency_employee(user)
        return employee.agency if employee else None

    class Meta:
        verbose_name = 'Сотрудник агентства'
        verbose_name_plural = 'Сотрудники агентств'
        permissions = [
            ('manage_employees', 'Пользователь может управлять сотрудниками агентства (#наше)'),
        ]
