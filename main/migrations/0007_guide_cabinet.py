# Generated by Django 3.2.1 on 2022-06-10 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_agencyemployeeavatar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tripworker',
            options={'permissions': [('manage_workers', 'Пользователь может управлять персональными данными водителей/гидов (#наше)'), ('create_guide_accounts', 'Пользователь может создавать аккаунты гидов (ссылки на личные кабинеты) (#наше)')], 'verbose_name': 'Работник тура (водитель/гид)', 'verbose_name_plural': 'Работники тура (водители/гиды)'},
        ),
        migrations.CreateModel(
            name='GuideCabinetLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cabinet_id', models.CharField(max_length=256, verbose_name='Ссылка - ID кабинета')),
                ('worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='guide_cabinet_link', to='main.tripworker')),
            ],
            options={
                'verbose_name': 'Ссылка на личный кабинет гида',
                'verbose_name_plural': 'Ссылки на личные кабинеты гидов',
            },
        ),
    ]