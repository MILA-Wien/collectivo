# Generated by Django 4.1.2 on 2022-10-20 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extensions', '0002_extension_description'),
        ('ux', '0004_remove_microfrontend_type_microfrontend_method_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('extension', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='extensions.extension')),
            ],
        ),
        migrations.RemoveField(
            model_name='microfrontend',
            name='method',
        ),
        migrations.AddField(
            model_name='microfrontend',
            name='type',
            field=models.CharField(choices=[('modules', 'JS remote entry for web components.'), ('html', 'Link to a normal html page.')], default='modules', max_length=50),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('label', models.CharField(max_length=255)),
                ('action', models.CharField(choices=[('default', 'Render microfrontend in the main application window.'), ('blank', 'Render microfrontend in a new page.')], max_length=50)),
                ('extension', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='extensions.extension')),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ux.menu')),
                ('microfrontend', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ux.microfrontend')),
            ],
        ),
    ]
