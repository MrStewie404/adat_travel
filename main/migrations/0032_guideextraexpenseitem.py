# Generated by Django 3.2.1 on 2023-05-10 14:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_add_hotelexpenseitem_booking'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuideExtraExpenseItem',
            fields=[
                ('parent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='guide_extra_expense_item', serialize=False, to='main.basepaymentexpenseitem')),
                ('day_number', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='День тура')),
            ],
            options={
                'verbose_name': 'Статья платежа - доп. расходы гида',
                'verbose_name_plural': 'Статьи платежей - доп. расходы гидов',
            },
            bases=('main.basepaymentexpenseitem',),
        ),
    ]