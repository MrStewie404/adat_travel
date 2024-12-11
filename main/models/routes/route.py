from django.db import models
from django.db.models import UniqueConstraint

from main.models.agency.agency import Agency
from main.models.custom_unique_error_mixin import CustomUniqueErrorMixin
from main.models.trips.abstract_trip import AbstractTrip
from main.models.utils import file_upload_path, replace_image_with_thumbnail


class RouteManager(models.Manager):
    def get_by_natural_key(self, name, agency__name):
        # Для упрощения ключей не сериализуем агенстство
        return self.get(name=name, agency=Agency.objects.get_by_natural_key(agency__name))


class Route(CustomUniqueErrorMixin, AbstractTrip):
    """Маршрут, шаблон путешествия."""
    agency = AbstractTrip.create_agency(related_name='routes')
    cities = AbstractTrip.create_cities(through='RouteAndCity', related_name='routes')
    services = AbstractTrip.create_services(through='RouteAndService', related_name='routes')
    duration_nights = AbstractTrip.create_duration_nights()
    image = models.ImageField('Фото', upload_to=file_upload_path, blank=True, null=True)
    short_description = models.CharField('Краткое описание', max_length=512, blank=True)

    objects = RouteManager()

    def natural_key(self):
        return (self.name,) + self.agency.natural_key()

    natural_key.dependencies = ['main.agency']

    def clean(self):
        if not self.image._committed:
            from main.models.abstract_media import AbstractMedia
            AbstractMedia.validate_file_size(self.image.file, max_size_mb=5)
            replace_image_with_thumbnail(self, 'image')
        super().clean()

    def save(self, *args, **kwargs):
        is_new = not self.pk
        self.full_clean()
        super().save(*args, **kwargs)
        if not is_new:
            # Удаляем лишние записи о днях тура и о посещениях городов (ночёвки - включая день отъезда)
            self.days.filter(day__gt=self.duration_days).delete()
            from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
            self.routeandcity_set.filter(day__gte=self.duration_days,
                                         objective=AbstractTripAndCity.ObjectiveEnum.OVERNIGHT).delete()
            self.routeandcity_set.filter(day__gt=self.duration_days,
                                         objective=AbstractTripAndCity.ObjectiveEnum.SIGHTSEEING).delete()

    def prepare_to_copy(self):
        self.pk = None  # Способ получить копию модели - просто сбрасываем первичный ключ
        self.image = None  # Иначе копия будет ссылаться на тот же самый файл

    def get_city(self, day_number, objective):
        route_and_city = self.routeandcity_set.filter(day=day_number, objective=objective).first()
        return route_and_city.city if route_and_city else None

    def cities_str(self):
        from main.models.trips.schedule.abstract_trip_and_city import AbstractTripAndCity
        sightseeing = AbstractTripAndCity.ObjectiveEnum.SIGHTSEEING
        all_names = [x.city.name for x in self.routeandcity_set.filter(objective=sightseeing).order_by('day')]
        non_repeating_names = [v for i, v in enumerate(all_names) if i == 0 or v != all_names[i - 1]]
        return ' · '.join(non_repeating_names)

    def may_delete(self):
        return not self.trips.exists()

    def get_tripandservice_set(self, day_number):
        """
        Возвращает отсортированный список моделей TripAndService
        (сортировка выполняется автоматически по полю order_id за счёт поля ordering в модели).
        """
        return self.routeandservice_set.filter(day=day_number)

    def get_unique_together_error_message(self):
        return "Шаблон тура с таким именем уже существует."

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(fields=['agency', 'name'], name='%(app_label)s_%(class)s_name_is_unique'),
        ]
        permissions = [
            ('manage_routes', 'Пользователь может управлять маршрутами (#наше)'),
        ]
