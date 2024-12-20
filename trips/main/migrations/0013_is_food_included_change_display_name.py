# Generated by Django 3.2.1 on 2022-06-28 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_trip_is_food_included'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='is_food_included',
            field=models.BooleanField(default=True, verbose_name='Учёт предпочтений по питанию'),
        ),
        migrations.AlterField(
            model_name='trip',
            name='is_food_included',
            field=models.BooleanField(default=True, verbose_name='Учёт предпочтений по питанию'),
        ),
    ]
