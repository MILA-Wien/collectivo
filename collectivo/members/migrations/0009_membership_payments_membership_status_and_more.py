# Generated by Django 4.1.7 on 2023-03-17 09:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_historicalmember_historicalmembership_and_more'),
        ('payments', '0001_initial'),
        ('emails', '0003_historicalemailtemplate_historicalemaildesign_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='payments',
            field=models.ManyToManyField(to='payments.payment'),
        ),
        migrations.AddField(
            model_name='membership',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.membershipstatus'),
        ),
        migrations.AddField(
            model_name='membership',
            name='subscriptions',
            field=models.ManyToManyField(to='payments.subscription'),
        ),
        migrations.AddField(
            model_name='membership',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.membershiptype'),
        ),
        migrations.AddField(
            model_name='historicalmembershiptype',
            name='comembership_of',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membershiptype'),
        ),
        migrations.AddField(
            model_name='historicalmembershiptype',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmembershiptype',
            name='welcome_mail',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='emails.emailtemplate'),
        ),
        migrations.AddField(
            model_name='historicalmembershipstatus',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmembershipstatus',
            name='type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membershiptype'),
        ),
        migrations.AddField(
            model_name='historicalmembershipcard',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmembershipcard',
            name='membership',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membership'),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='comembership_of',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membership'),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='member',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.member'),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='status',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membershipstatus'),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='type',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='members.membershiptype'),
        ),
        migrations.AddField(
            model_name='historicalmember',
            name='history_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalmember',
            name='user',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
