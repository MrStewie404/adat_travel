from django.db import models

from main.models.services.service import Service


class AbstractTripAndService(models.Model):
    """Абстрактная модель: услуга в туре (или на маршруте)."""
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField('День тура', blank=True, null=True)
    order_id = models.SmallIntegerField(default=-1)

    def trip_or_route(self):
        if hasattr(self, 'trip'):
            return getattr(self, 'trip')
        return getattr(self, 'route', None)

    def save(self, *args, **kwargs):
        if not self.pk and self.order_id < 0:
            query_set = self.__class__.objects.all()
            if hasattr(self, 'trip'):
                query_set = query_set.filter(trip=self.trip)
            elif hasattr(self, 'route'):
                query_set = query_set.filter(route=self.route)
            max_id = query_set.filter(day=self.day).aggregate(max_id=models.Max('order_id'))['max_id']
            self.order_id = max(max_id + 1, 0) if max_id is not None else 0
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ('order_id',)  # TODO: добавить day в order (а может, и service тоже)
