from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from main.models.clients.person import Person
from main.models.utils import file_upload_path, replace_image_with_thumbnail


class TripWorker(Person):
    """Работник тура (водитель/гид)."""

    class RoleEnum(models.TextChoices):
        GUIDE = 'GUIDE', 'Гид'
        DRIVER = 'DRIVER', 'Водитель'
        DRIVER_GUIDE = 'DRIVER_GUIDE', 'Гид-водитель'

        __empty__ = '(Выберите специализацию)'

    person = models.OneToOneField(Person, on_delete=models.CASCADE, parent_link=True, related_name='trip_worker')
    role = models.CharField(
        'Специализация',
        max_length=16,
        choices=RoleEnum.choices,
        blank=False
    )
    money_account = models.ForeignKey('BaseMoneyAccount', on_delete=models.PROTECT, related_name='trip_workers',
                                      blank=True, null=True)
    image = models.ImageField('Фото', upload_to=file_upload_path, blank=True, null=True)

    def __str__(self):
        return self.full_name()

    @property
    def name_with_role(self):
        role_str = self.RoleEnum(self.role).label
        return f"{self.full_name()} - {role_str}"

    def try_get_driver_info(self):
        return getattr(self, 'driver_info', None)

    def try_get_cabinet_link(self):
        return getattr(self, 'guide_cabinet_link', None)

    def clean(self):
        if not self.image._committed:
            from main.models.abstract_media import AbstractMedia
            AbstractMedia.validate_file_size(self.image.file, max_size_mb=15)
            replace_image_with_thumbnail(self, 'image')
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def create_driver(agency, name, **kwargs):
        return TripWorker.objects.create(agency=agency, name=name, role=TripWorker.RoleEnum.DRIVER, **kwargs)

    @staticmethod
    def create_guide(agency, name, **kwargs):
        return TripWorker.objects.create(agency=agency, name=name, role=TripWorker.RoleEnum.GUIDE, **kwargs)

    class Meta:
        verbose_name = 'Работник тура (водитель/гид)'
        verbose_name_plural = 'Работники тура (водители/гиды)'
        permissions = [
            ('manage_workers', 'Пользователь может управлять персональными данными водителей/гидов (#наше)'),
            ('manage_guide_accounts', 'Пользователь может управлять аккаунтами гидов (личными кабинетами) (#наше)'),
        ]


@receiver(post_delete, sender='main.TripWorker')
def post_delete_worker(sender, instance, **kwargs):
    from main.models.trips.accommodation.abstract_trip_roommates_group import AbstractTripRoommatesGroup
    for group in instance.roommate_groups.all():
        AbstractTripRoommatesGroup.remove_from_roommates_group(instance, group)
