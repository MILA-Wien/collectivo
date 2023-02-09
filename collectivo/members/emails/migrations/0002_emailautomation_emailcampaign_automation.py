# Generated by Django 4.1.6 on 2023-02-09 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAutomation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('trigger', models.CharField(choices=[('new_member', 'new_member')], max_length=10)),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.emailtemplate')),
            ],
        ),
        migrations.AddField(
            model_name='emailcampaign',
            name='automation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.emailautomation'),
        ),
    ]
