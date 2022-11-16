# Generated by Django 4.1.2 on 2022-10-20 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ux', '0003_alter_microfrontend_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='microfrontend',
            name='type',
        ),
        migrations.AddField(
            model_name='microfrontend',
            name='method',
            field=models.CharField(choices=[('modules', 'Integration of web components via remote entry.'), ('iframe', 'Integration of target link as an iframe.')], default='modules', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='microfrontend',
            name='path',
            field=models.URLField(max_length=255),
        ),
    ]