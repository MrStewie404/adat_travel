# Generated by Django 3.2.1 on 2022-06-14 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_guide_cabinet'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tripworker',
            options={'permissions': [('manage_workers', 'Пользователь может управлять персональными данными водителей/гидов (#наше)'), ('manage_guide_accounts', 'Пользователь может управлять аккаунтами гидов (личными кабинетами) (#наше)')], 'verbose_name': 'Работник тура (водитель/гид)', 'verbose_name_plural': 'Работники тура (водители/гиды)'},
        ),
    ]