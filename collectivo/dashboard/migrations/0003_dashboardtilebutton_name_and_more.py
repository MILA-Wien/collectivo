# Generated by Django 4.1.8 on 2023-04-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_dashboardtilebutton_dashboardtile_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardtilebutton',
            name='name',
            field=models.CharField(default=None, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='historicaldashboardtilebutton',
            name='name',
            field=models.CharField(db_index=True, default=None, max_length=255, null=True),
        ),
    ]
