# Generated by Django 3.2.1 on 2023-06-09 07:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_guideextraexpenseitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierCommissionExpenseItem',
            fields=[
                ('parent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='supplier_commission_expense_item', serialize=False, to='main.basepaymentexpenseitem')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_expense_items', to='main.supplier')),
                ('trip_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commission_expense_items', to='main.tripcompany')),
            ],
            options={
                'verbose_name': 'Статья платежа - комиссия контрагенту',
                'verbose_name_plural': 'Статьи платежей - комиссии контрагентам',
            },
            bases=('main.basepaymentexpenseitem',),
        ),
    ]