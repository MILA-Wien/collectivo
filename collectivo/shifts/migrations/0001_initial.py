# Generated by Django 4.1.6 on 2023-02-03 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_shift_date', models.DateField(max_length=30)),
                ('shift_type', models.CharField(choices=[('fixed', 'fixed'), ('open', 'open')], default='fixed', help_text='Type of shift. Fixed shifts are set automatically every month to one or many users. Open shifts are not addressed to a user yet.', max_length=20)),
                ('shift_week', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A', help_text='A month is divided in four shift weeks: A, B, C, D', max_length=2)),
                ('starting_time', models.DateTimeField()),
                ('duration', models.FloatField(default=3)),
                ('end_time', models.DateTimeField()),
                ('required_users', models.IntegerField(default=2)),
                ('shift_day', models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], default='Monday', help_text='Shift days are necessary for fixed shifts to registeri.e. every monday on Week A', max_length=20)),
                ('additional_info_general', models.TextField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='ShiftUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shift_creator', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='IndividualShift',
            fields=[
                ('generalshift_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shifts.generalshift')),
                ('user_has_attended', models.BooleanField(default=False)),
                ('additional_info_individual', models.TextField(max_length=300)),
                ('assigned_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shifts.shiftuser')),
            ],
            bases=('shifts.generalshift',),
        ),
        migrations.AddField(
            model_name='generalshift',
            name='individual_shifts',
            field=models.ManyToManyField(blank=True, related_name='%(class)s_individual_shifts', to='shifts.individualshift'),
        ),
    ]
