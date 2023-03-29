# Generated by Django 4.1.7 on 2023-03-28 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extensions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='built_in',
            field=models.BooleanField(default=False, help_text='Whether the extension is part of collectivo.'),
        ),
        migrations.AddField(
            model_name='extension',
            name='label',
            field=models.CharField(blank=True, help_text='Label to display the extension.', max_length=255),
        ),
        migrations.AlterField(
            model_name='extension',
            name='active',
            field=models.BooleanField(default=True, help_text='Whether the extension is active.'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the extension and its features.'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='name',
            field=models.CharField(help_text='Unique name of the extension.', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='extension',
            name='version',
            field=models.CharField(blank=True, help_text='Version of the extension.', max_length=255),
        ),
    ]