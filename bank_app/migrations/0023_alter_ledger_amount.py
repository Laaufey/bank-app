# Generated by Django 4.0.5 on 2022-06-07 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0022_alter_ledger_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
