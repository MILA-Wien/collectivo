# Generated by Django 4.1.7 on 2023-03-29 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('extensions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='payment_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bank_account_iban', models.CharField(blank=True, max_length=255, null=True)),
                ('bank_account_owner', models.CharField(blank=True, max_length=255, null=True)),
                ('payment_method', models.CharField(choices=[('transfer', 'transfer'), ('sepa', 'sepa')], max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('extension', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='extensions.extension')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('status', models.CharField(choices=[('draft', 'draft'), ('paused', 'paused'), ('active', 'active'), ('ended', 'ended')], default='draft', max_length=10)),
                ('date_started', models.DateField(blank=True, null=True)),
                ('date_ended', models.DateField(blank=True, null=True)),
                ('repeat_each', models.IntegerField(default=1)),
                ('repeat_unit', models.CharField(choices=[('year', 'year'), ('month', 'month'), ('week', 'week'), ('day', 'day')], max_length=10)),
                ('extension', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='extensions.extension')),
                ('payer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.paymentprofile')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payments.paymenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('status', models.CharField(choices=[('draft', 'draft'), ('pending', 'pending'), ('success', 'success'), ('canceled', 'canceled'), ('failure', 'failure')], default='draft', max_length=10)),
                ('date_due', models.DateField(null=True)),
                ('date_paid', models.DateField(null=True)),
                ('extension', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='extensions.extension')),
                ('payer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.paymentprofile')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='payments.subscription')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='payments.paymenttype')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalSubscription',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('status', models.CharField(choices=[('draft', 'draft'), ('paused', 'paused'), ('active', 'active'), ('ended', 'ended')], default='draft', max_length=10)),
                ('date_started', models.DateField(blank=True, null=True)),
                ('date_ended', models.DateField(blank=True, null=True)),
                ('repeat_each', models.IntegerField(default=1)),
                ('repeat_unit', models.CharField(choices=[('year', 'year'), ('month', 'month'), ('week', 'week'), ('day', 'day')], max_length=10)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('extension', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='extensions.extension')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.paymentprofile')),
                ('type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.paymenttype')),
            ],
            options={
                'verbose_name': 'historical subscription',
                'verbose_name_plural': 'historical subscriptions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPaymentProfile',
            fields=[
                ('bank_account_iban', models.CharField(blank=True, max_length=255, null=True)),
                ('bank_account_owner', models.CharField(blank=True, max_length=255, null=True)),
                ('payment_method', models.CharField(choices=[('transfer', 'transfer'), ('sepa', 'sepa')], max_length=30)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical payment profile',
                'verbose_name_plural': 'historical payment profiles',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPayment',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('status', models.CharField(choices=[('draft', 'draft'), ('pending', 'pending'), ('success', 'success'), ('canceled', 'canceled'), ('failure', 'failure')], default='draft', max_length=10)),
                ('date_due', models.DateField(null=True)),
                ('date_paid', models.DateField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('extension', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='extensions.extension')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('payer', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.paymentprofile')),
                ('subscription', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.subscription')),
                ('type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.paymenttype')),
            ],
            options={
                'verbose_name': 'historical payment',
                'verbose_name_plural': 'historical payments',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
