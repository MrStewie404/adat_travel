# Generated by Django 3.2.1 on 2023-08-02 13:59

from django.db import migrations


def set_default_values(apps, schema_editor):
    """Исправленная инициализация поля is_visible_for_suppliers - устанавливаем флаг только в регулярных турах."""
    # We can't import the Trip model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Trip = apps.get_model('main', 'Trip')
    for trip in Trip.objects.all():
        trip.is_visible_for_supplier = trip.category == 'REGULAR'
        trip.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_supplier_default_commission'),
    ]

    operations = [
        migrations.RunPython(set_default_values, elidable=True),
    ]