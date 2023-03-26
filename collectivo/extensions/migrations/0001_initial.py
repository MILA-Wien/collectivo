# Generated by Django 4.1.7 on 2023-03-24 12:52

import collectivo.utils.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('version', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
            bases=(models.Model, collectivo.utils.models.RegisterMixin),
        ),
    ]
