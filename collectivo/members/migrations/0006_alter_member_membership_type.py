# Generated by Django 4.1.6 on 2023-02-15 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_remove_member_email_verified_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='membership_type',
            field=models.CharField(choices=[('active', 'active'), ('investing', 'investing'), ('no member', 'no member')], max_length=20),
        ),
    ]
