# Generated by Django 3.2.1 on 2024-04-18 14:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_agencypaymenttoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='default_prepayment',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Аванс'),
        ),
    ]
