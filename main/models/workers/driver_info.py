from django.db import models

from main.models.workers.trip_worker import TripWorker


class DriverInfoManager(models.Manager):
    def get_by_natural_key(self, *driver_args):
        return self.get(
            driver=TripWorker.objects.get_by_natural_key(*driver_args),
        )


class DriverInfo(models.Model):
    """Данные о водителе."""
    driver = models.OneToOneField(TripWorker, on_delete=models.CASCADE, related_name='driver_info')
    driver_license_number = models.CharField('Водительское удостоверение', max_length=32, blank=True)
    car_number = models.CharField('Госномер', max_length=32, blank=True)

    objects = DriverInfoManager()

    def natural_key(self):
        return self.driver.natural_key()

    natural_key.dependencies = ['main.tripworker']

    def __str__(self):
        return f"{self.driver}: {self.driver_license_number}, {self.car_number}"

    class Meta:
        verbose_name = 'Данные о водителе'
        verbose_name_plural = 'Данные о водителях'
