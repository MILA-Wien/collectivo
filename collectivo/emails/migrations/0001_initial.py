# Generated by Django 4.1.7 on 2023-03-24 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extensions', '0001_initial'),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailDesign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique='True')),
                ('body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique='True')),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('design', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.emaildesign')),
                ('tag', models.ForeignKey(help_text='This tag will be added to recipients if campaign is sent.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='tags.tag')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalEmailTemplate',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('design', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='emails.emaildesign')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('tag', models.ForeignKey(blank=True, db_constraint=False, help_text='This tag will be added to recipients if campaign is sent.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tags.tag')),
            ],
            options={
                'verbose_name': 'historical email template',
                'verbose_name_plural': 'historical email templates',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEmailDesign',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('body', models.TextField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical email design',
                'verbose_name_plural': 'historical email designs',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEmailCampaign',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'draft'), ('pending', 'pending'), ('success', 'success'), ('failure', 'failure')], default='draft', max_length=10)),
                ('status_message', models.CharField(max_length=255, null=True)),
                ('sent', models.DateTimeField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('extension', models.ForeignKey(blank=True, db_constraint=False, help_text='The extension that created this campaign.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='extensions.extension')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='emails.emailtemplate')),
            ],
            options={
                'verbose_name': 'historical email campaign',
                'verbose_name_plural': 'historical email campaigns',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('draft', 'draft'), ('pending', 'pending'), ('success', 'success'), ('failure', 'failure')], default='draft', max_length=10)),
                ('status_message', models.CharField(max_length=255, null=True)),
                ('sent', models.DateTimeField(null=True)),
                ('extension', models.ForeignKey(blank=True, help_text='The extension that created this campaign.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='extensions.extension')),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.emailtemplate')),
            ],
        ),
    ]
