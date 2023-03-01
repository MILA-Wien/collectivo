# Generated by Django 4.1.7 on 2023-03-01 14:50

import collectivo.utils.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extensions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('label', models.CharField(max_length=255)),
                ('requires_permission', models.CharField(max_length=255)),
                ('target', models.CharField(choices=[('main', 'main'), ('blank', 'blank')], default='main', max_length=50)),
                ('component', models.CharField(max_length=255, null=True)),
                ('link', models.URLField(null=True)),
                ('order', models.FloatField(default=1)),
                ('style', models.CharField(choices=[('normal', 'normal')], default='normal', max_length=50)),
                ('icon_name', models.CharField(max_length=255, null=True)),
                ('icon_path', models.URLField(null=True)),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extensions.extension')),
                ('items', models.ManyToManyField(to='menus.menuitem')),
            ],
            options={
                'unique_together': {('name', 'extension')},
            },
            bases=(models.Model, collectivo.utils.models.RegisterMixin),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extensions.extension')),
                ('items', models.ManyToManyField(to='menus.menuitem')),
            ],
            options={
                'unique_together': {('name', 'extension')},
            },
            bases=(models.Model, collectivo.utils.models.RegisterMixin),
        ),
    ]
