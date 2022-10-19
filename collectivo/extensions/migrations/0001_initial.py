# Generated by Django 4.1.2 on 2022-10-17 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('version', models.CharField(blank=True, max_length=50)),
            ],
        ),
    ]