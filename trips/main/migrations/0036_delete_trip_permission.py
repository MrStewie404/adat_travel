# Generated by Django 3.2.1 on 2023-08-02 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_trip_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trip',
            options={'permissions': [('plan_trips', 'Пользователь может планировать туры (#наше)'), ('delete_trips', 'Пользователь может удалять туры (#наше)'), ('manage_trip_status', 'Пользователь может редактировать статусы туров (#наше)'), ('manage_trip_tourists', 'Пользователь может редактировать гостей в турах (#наше)'), ('manage_trip_staff', 'Пользователь может редактировать гидов/водителей в турах (#наше)'), ('manage_trip_accommodation', 'Пользователь может управлять расселением гостей (#наше)'), ('view_trip_accommodation', 'Пользователь может просматривать страницу с расселением гостей (#наше)'), ('print_trip_reports', 'Пользователь может печатать отчёты по туру (#наше)'), ('print_client_contracts', 'Пользователь может печатать туристические договоры (#наше)'), ('manage_money_statistics', 'Пользователь может просматривать финансовую информацию по турам (#наше)')], 'verbose_name': 'Тур', 'verbose_name_plural': 'Туры'},
        ),
    ]
