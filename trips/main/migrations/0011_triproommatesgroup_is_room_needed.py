# Generated by Django 3.2.1 on 2022-06-21 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_guide_cabinet_add_short_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='triproommatesgroup',
            name='is_room_needed',
            field=models.BooleanField(default=True, verbose_name='Нужен номер'),
        ),
    ]