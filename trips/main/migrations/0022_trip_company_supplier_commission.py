# Generated by Django 3.2.1 on 2023-03-21 14:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_clientcontract_contract_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripcompany',
            name='commission_type',
            field=models.PositiveSmallIntegerField(choices=[(None, '(Выберите вид комиссии)'), (1, 'Фиксированная (в рублях)'), (2, 'В % от суммы договора')], default=2, verbose_name='Вид комиссии'),
        ),
        migrations.AddField(
            model_name='tripcompany',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trip_companies', to='main.supplier'),
        ),
        migrations.AddField(
            model_name='tripcompany',
            name='supplier_commission',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Величина комиссии'),
        ),
    ]
