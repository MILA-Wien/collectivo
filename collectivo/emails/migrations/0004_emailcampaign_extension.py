# Generated by Django 4.1.7 on 2023-03-15 10:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extensions', '0001_initial'),
        ('emails', '0003_remove_emailautomationtrigger_extension_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcampaign',
            name='extension',
            field=models.ForeignKey(blank=True, help_text='The extension that created this campaign.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='extensions.extension'),
        ),
    ]
