# Generated by Django 4.1.7 on 2023-04-07 06:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extensions', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardtile',
            name='content',
            field=models.TextField(blank=True, help_text='HTML content to display inside the tile.', null=True),
        ),
        migrations.AddField(
            model_name='dashboardtile',
            name='source',
            field=models.CharField(choices=[('db', 'Content is defined in the content field of this model.'), ('component', 'Content is defined in a webcomponent.')], default='component', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dashboardtile',
            name='extension',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='extensions.extension'),
        ),
        migrations.AlterField(
            model_name='dashboardtile',
            name='label',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='dashboardtile',
            name='requires_group',
            field=models.ForeignKey(blank=True, help_text='If set, the object will only be displayed to users with this group.', null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
    ]