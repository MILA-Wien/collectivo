# Generated by Django 4.1.7 on 2023-03-29 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tags', '0001_initial'),
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplateTag',
            fields=[
                ('template', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tag', serialize=False, to='emails.emailtemplate')),
                ('tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='email_templates', to='tags.tag')),
            ],
        ),
    ]
