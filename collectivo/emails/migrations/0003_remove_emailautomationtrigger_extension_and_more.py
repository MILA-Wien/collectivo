# Generated by Django 4.1.7 on 2023-03-15 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailautomationtrigger',
            name='extension',
        ),
        migrations.RemoveField(
            model_name='emailcampaign',
            name='automation',
        ),
        migrations.DeleteModel(
            name='EmailAutomation',
        ),
        migrations.DeleteModel(
            name='EmailAutomationTrigger',
        ),
    ]