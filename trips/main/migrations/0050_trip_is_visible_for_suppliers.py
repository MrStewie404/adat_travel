# Generated by Django 3.2.1 on 2024-01-31 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_supplier_cabinet'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='is_visible_for_suppliers',
            field=models.BooleanField(default=False, verbose_name='Показывать в кабинетах контрагентов'),
        ),
    ]
