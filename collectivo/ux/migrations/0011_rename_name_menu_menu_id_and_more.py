# Generated by Django 4.1.3 on 2022-11-02 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ux', '0010_remove_menuitem_microfrontend_delete_microfrontend'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menu',
            old_name='name',
            new_name='menu_id',
        ),
        migrations.RenameField(
            model_name='menuitem',
            old_name='name',
            new_name='item_id',
        ),
    ]