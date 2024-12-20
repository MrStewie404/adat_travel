# Generated by Django 3.2.1 on 2022-06-06 07:55
import logging

from django.db import migrations, models


def fill_agency(apps, schema_editor):
    """
    Заполняем новое поле "агентство" в городах, гостиницах и ресторанах.
    Так как у нас на данный момент все эти сущности создавались только для агентства АДАТ,
    то к нему и привязываем все существующие в БД объекты.
    """
    # We can't import the following models directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Agency = apps.get_model('main', 'Agency')
    City = apps.get_model('main', 'City')
    Hotel = apps.get_model('main', 'Hotel')
    Restaurant = apps.get_model('main', 'Restaurant')
    agency = Agency.objects.filter(models.Q(name='АДАТ') | models.Q(name='Адат')).first()
    if not agency:
        logging.warning(
            "Агентство АДАТ не найдено в БД. "
            "Все созданные города, гостиницы и рестораны останутся общими для всех агентств."
        )
        return
    for city in City.objects.filter(agency__isnull=True):
        city.agency = agency
        city.save()
    for hotel in Hotel.objects.filter(agency__isnull=True):
        hotel.agency = agency
        hotel.save()
    for restaurant in Restaurant.objects.filter(agency__isnull=True):
        restaurant.agency = agency
        restaurant.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_agency_in_cities_hotels_restaurants'),
    ]

    operations = [
        migrations.RunPython(fill_agency, elidable=True),
    ]
