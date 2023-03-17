# Generated by Django 4.1.7 on 2023-03-17 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_paymenttype_alter_historicalpayment_name_and_more'),
        ('members', '0014_rename_fees_custom_historicalmembershiptype_fees_amount_custom_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalmembership',
            name='fees',
        ),
        migrations.RemoveField(
            model_name='historicalmembership',
            name='shares',
        ),
        migrations.RemoveField(
            model_name='historicalmembership',
            name='shares_not_paid',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='fees',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='payments',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='shares',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='shares_not_paid',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='subscriptions',
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='fees_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=100),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='fees_subscription',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='payments.subscription'),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='shares_paid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='historicalmembership',
            name='shares_signed',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='membership',
            name='fees_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=100),
        ),
        migrations.AddField(
            model_name='membership',
            name='fees_subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='membership_fees', to='payments.subscription'),
        ),
        migrations.AddField(
            model_name='membership',
            name='shares_paid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='membership',
            name='shares_payments',
            field=models.ManyToManyField(related_name='membership_shares', to='payments.payment'),
        ),
        migrations.AddField(
            model_name='membership',
            name='shares_signed',
            field=models.PositiveIntegerField(default=0),
        ),
    ]