# Generated by Django 4.1.7 on 2023-05-02 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='target',
            field=models.CharField(choices=[('main', 'main'), ('blank', 'blank'), ('iframe', 'iframe')], default='main', max_length=50),
        ),
    ]
