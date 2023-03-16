# Generated by Django 4.1.7 on 2023-03-16 09:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0005_alter_historicalpaymentprofile_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='payments', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
