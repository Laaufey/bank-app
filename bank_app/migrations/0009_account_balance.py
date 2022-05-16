# Generated by Django 4.0.3 on 2022-05-12 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_app', '0008_remove_account_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]
