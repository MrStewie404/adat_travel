# Generated by Django 3.2.1 on 2023-08-02 13:59

from django.db import migrations


def set_default_values(apps, schema_editor):
    """Устанавливаем во всех турах и экскурсиях флаг is_visible_for_suppliers."""
    # We can't import the Trip model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Trip = apps.get_model('main', 'Trip')
    for trip in Trip.objects.all():
        trip.is_visible_for_supplier = True
        trip.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_trip_is_visible_for_suppliers'),
    ]

    operations = [
        migrations.RunPython(set_default_values, elidable=True),
    ]