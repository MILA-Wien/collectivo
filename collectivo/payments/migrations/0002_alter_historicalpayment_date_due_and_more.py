# Generated by Django 4.1.7 on 2023-03-28 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpayment',
            name='date_due',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='historicalpayment',
            name='date_paid',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date_due',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='date_paid',
            field=models.DateField(null=True),
        ),
    ]
