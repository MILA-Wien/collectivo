# Generated by Django 4.1.2 on 2022-10-20 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ux', '0007_alter_menuitem_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='action',
            field=models.CharField(choices=[('default', 'Render microfrontend in the main app window.'), ('blank', 'Render microfrontend in a new page.')], default='default', max_length=50),
        ),
    ]
