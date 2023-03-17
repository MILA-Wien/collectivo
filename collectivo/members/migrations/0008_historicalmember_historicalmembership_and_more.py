# Generated by Django 4.1.7 on 2023-03-17 09:46

from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0003_historicalemailtemplate_historicalemaildesign_and_more'),
        ('members', '0007_remove_member_id_remove_member_user_id_member_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalMember',
            fields=[
                ('person_type', models.CharField(choices=[('natural', 'natural'), ('legal', 'legal')], default='natural', help_text='Type of person.', max_length=20)),
                ('gender', models.CharField(choices=[('diverse', 'diverse'), ('female', 'female'), ('male', 'male')], default='diverse', max_length=20)),
                ('address_street', models.CharField(max_length=255)),
                ('address_number', models.CharField(max_length=255)),
                ('address_stair', models.CharField(blank=True, max_length=255, null=True)),
                ('address_door', models.CharField(blank=True, max_length=255, null=True)),
                ('address_postcode', models.CharField(max_length=255)),
                ('address_city', models.CharField(max_length=255)),
                ('address_country', models.CharField(max_length=255)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('legal_name', models.CharField(blank=True, max_length=255, null=True)),
                ('legal_type', models.CharField(blank=True, max_length=255, null=True)),
                ('legal_id', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical member',
                'verbose_name_plural': 'historical members',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMembership',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('number', models.IntegerField(db_index=True)),
                ('active', models.BooleanField(default=False)),
                ('started', models.DateField(blank=True, null=True)),
                ('cancelled', models.DateField(blank=True, null=True)),
                ('ended', models.DateField(blank=True, null=True)),
                ('shares_not_payed', models.IntegerField(blank=True, null=True)),
                ('shares', models.IntegerField(blank=True, null=True)),
                ('fees', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical membership',
                'verbose_name_plural': 'historical memberships',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMembershipCard',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('date_created', models.DateField()),
                ('active', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical membership card',
                'verbose_name_plural': 'historical membership cards',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMembershipStatus',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical membership status',
                'verbose_name_plural': 'historical membership statuss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalMembershipType',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('has_shares', models.BooleanField(default=False)),
                ('shares_price', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('shares_number_custom', models.BooleanField(default=False)),
                ('shares_number_custom_min', models.IntegerField(blank=True, null=True)),
                ('shares_number_standard', models.IntegerField(blank=True, null=True)),
                ('shares_number_social', models.IntegerField(blank=True, null=True)),
                ('has_fees', models.BooleanField(default=False)),
                ('fees_custom', models.BooleanField(default=False)),
                ('fees_repeat_each', models.IntegerField(default=1)),
                ('fees_repeat_unit', models.CharField(choices=[('year', 'year'), ('month', 'month'), ('week', 'week'), ('day', 'day')], default='year', max_length=20)),
                ('fees_custom_min', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('fees_standard', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('fees_social', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('has_card', models.BooleanField(default=False)),
                ('comembership_max', models.IntegerField(blank=True, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical membership type',
                'verbose_name_plural': 'historical membership types',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
                ('active', models.BooleanField(default=False)),
                ('started', models.DateField(blank=True, null=True)),
                ('cancelled', models.DateField(blank=True, null=True)),
                ('ended', models.DateField(blank=True, null=True)),
                ('shares_not_payed', models.IntegerField(blank=True, null=True)),
                ('shares', models.IntegerField(blank=True, null=True)),
                ('fees', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('comembership_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.membership')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField()),
                ('active', models.BooleanField(default=False)),
                ('membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.membership')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MembershipType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('has_shares', models.BooleanField(default=False)),
                ('shares_price', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('shares_number_custom', models.BooleanField(default=False)),
                ('shares_number_custom_min', models.IntegerField(blank=True, null=True)),
                ('shares_number_standard', models.IntegerField(blank=True, null=True)),
                ('shares_number_social', models.IntegerField(blank=True, null=True)),
                ('has_fees', models.BooleanField(default=False)),
                ('fees_custom', models.BooleanField(default=False)),
                ('fees_repeat_each', models.IntegerField(default=1)),
                ('fees_repeat_unit', models.CharField(choices=[('year', 'year'), ('month', 'month'), ('week', 'week'), ('day', 'day')], default='year', max_length=20)),
                ('fees_custom_min', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('fees_standard', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('fees_social', models.DecimalField(blank=True, decimal_places=2, max_digits=100, null=True)),
                ('has_card', models.BooleanField(default=False)),
                ('comembership_max', models.IntegerField(blank=True, null=True)),
                ('comembership_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.membershiptype')),
                ('welcome_mail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.emailtemplate')),
            ],
        ),
        migrations.RenameField(
            model_name='member',
            old_name='admin_notes',
            new_name='notes',
        ),
        migrations.RemoveField(
            model_name='member',
            name='bank_account_iban',
        ),
        migrations.RemoveField(
            model_name='member',
            name='bank_account_owner',
        ),
        migrations.RemoveField(
            model_name='member',
            name='children',
        ),
        migrations.RemoveField(
            model_name='member',
            name='coshopper',
        ),
        migrations.RemoveField(
            model_name='member',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='member',
            name='groups_interested',
        ),
        migrations.RemoveField(
            model_name='member',
            name='membership_cancelled',
        ),
        migrations.RemoveField(
            model_name='member',
            name='membership_card',
        ),
        migrations.RemoveField(
            model_name='member',
            name='membership_end',
        ),
        migrations.RemoveField(
            model_name='member',
            name='membership_start',
        ),
        migrations.RemoveField(
            model_name='member',
            name='membership_type',
        ),
        migrations.RemoveField(
            model_name='member',
            name='shares_number',
        ),
        migrations.RemoveField(
            model_name='member',
            name='shares_payment_date',
        ),
        migrations.RemoveField(
            model_name='member',
            name='shares_payment_type',
        ),
        migrations.RemoveField(
            model_name='member',
            name='skills',
        ),
        migrations.RemoveField(
            model_name='member',
            name='survey_contact',
        ),
        migrations.RemoveField(
            model_name='member',
            name='survey_motivation',
        ),
        migrations.RemoveField(
            model_name='member',
            name='tags',
        ),
        migrations.AlterField(
            model_name='member',
            name='address_city',
            field=models.CharField(default='undefined', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='address_country',
            field=models.CharField(default='undefined', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='address_number',
            field=models.CharField(default='undefined', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='address_postcode',
            field=models.CharField(default='undefined', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='member',
            name='address_street',
            field=models.CharField(default='undefined', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='MemberAddon',
        ),
        migrations.DeleteModel(
            name='MemberCard',
        ),
        migrations.DeleteModel(
            name='MemberGroup',
        ),
        migrations.DeleteModel(
            name='MemberSkill',
        ),
        migrations.DeleteModel(
            name='MemberTag',
        ),
        migrations.AddField(
            model_name='membershipstatus',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.membershiptype'),
        ),
        migrations.AddField(
            model_name='membership',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='members.member'),
        ),
    ]