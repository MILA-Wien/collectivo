# Generated by Django 4.1.8 on 2023-05-02 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lotzapp', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0002_account_historicalinvoice_historicalitemtype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lotzappinvoice',
            name='invoice',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lotzapp', to='payments.invoice'),
        ),
        migrations.AddField(
            model_name='lotzappaddress',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lotzapp', to=settings.AUTH_USER_MODEL),
        ),
    ]
