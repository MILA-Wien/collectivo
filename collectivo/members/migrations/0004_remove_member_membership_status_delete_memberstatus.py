# Generated by Django 4.1.5 on 2023-01-30 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0003_membertag_built_in'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='membership_status',
        ),
        migrations.DeleteModel(
            name='MemberStatus',
        ),
    ]
