# Generated by Django 3.2.1 on 2024-07-11 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0074_alter_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='auto_update_schedule',
            field=models.BooleanField(default=False, verbose_name='Автоматически обновлять услуги и дни из шаблона'),
        ),
    ]