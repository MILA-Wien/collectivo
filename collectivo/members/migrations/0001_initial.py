from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.UUIDField(null=True, unique=True)),
                ('email_verified', models.BooleanField()),
                ('membership_type', models.CharField(choices=[('active', 'active'), ('investing', 'investing'), ('legal', 'legal')], default='active', help_text='Type of membership.', max_length=20)),
                ('membership_status', models.CharField(choices=[('1_applicant', '1_applicant'), ('2_provisional', '2_provisional'), ('3_approved', '3_approved'), ('4_normal', '4_normal'), ('5_leaving', '5_leaving'), ('6_left', '6_left'), ('7_deceased', '7_deceased')], default='1_applicant', help_text='Current status of membership.', max_length=20)),
                ('shares_number', models.IntegerField(default=0)),
                ('shares_payment_status', models.CharField(choices=[('1_pending', '1_pending'), ('2_processing', '2_processing'), ('3_success', '3_success'), ('4_denied', '4_denied')], default='1_pending', help_text='Status of payment.', max_length=20)),
                ('shares_payment_type', models.CharField(choices=[('sepa', 'sepa')], default='sepa', help_text='Type of payment.', max_length=20)),
                ('shares_installment_plan', models.BooleanField(default=False)),
                ('title_pre', models.CharField(max_length=255, null=True)),
                ('title_post', models.CharField(max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female'), ('diverse', 'diverse')], max_length=20, null=True)),
                ('date_birth', models.DateField(null=True)),
                ('address_street', models.CharField(max_length=255, null=True)),
                ('address_number', models.CharField(max_length=255, null=True)),
                ('address_is_home', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=20, null=True)),
                ('address_co', models.CharField(max_length=255, null=True)),
                ('address_stair', models.CharField(max_length=255, null=True)),
                ('address_door', models.CharField(max_length=255, null=True)),
                ('address_postcode', models.CharField(max_length=255, null=True)),
                ('address_city', models.CharField(max_length=255, null=True)),
                ('address_country', models.CharField(max_length=255, null=True)),
                ('phone', models.CharField(max_length=255, null=True)),
                ('phone_2', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('email_2', models.EmailField(max_length=254, null=True)),
                ('homepage', models.CharField(max_length=255, null=True)),
                ('legal_name', models.CharField(max_length=255, null=True)),
                ('legal_type', models.CharField(max_length=255, null=True)),
                ('legal_seat', models.CharField(max_length=255, null=True)),
                ('legal_type_id', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
