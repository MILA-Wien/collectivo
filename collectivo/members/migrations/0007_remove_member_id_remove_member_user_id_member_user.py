# Generated by Django 4.1.7 on 2023-03-02 16:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


# TODO: Test this migration before production.
def switch_from_user_id_to_user(apps, schema_editor):
    """Transfer data from user_id to user."""
    Member = apps.get_model("members", "Member")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    db_alias = schema_editor.connection.alias
    for member in Member.objects.using(db_alias).all():
        user = User.objects.using(db_alias).create(
            username=member.email,
            email=member.email,
            first_name=member.first_name,
            last_name=member.last_name,
        )
        member.user = user
        member.save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("members", "0006_alter_member_membership_type"),
    ]

    operations = [
        migrations.RenameField(
            model_name="member",
            old_name="user_id",
            new_name="old_user_id",
        ),
        migrations.RemoveField(
            model_name="member",
            name="id",
        ),
        migrations.AddField(
            model_name="member",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                primary_key=True,
                serialize=False,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(switch_from_user_id_to_user, None),
        migrations.RemoveField(
            model_name="member",
            name="old_user_id",
        ),
        migrations.RemoveField(
            model_name="member",
            name="email",
        ),
        migrations.RemoveField(
            model_name="member",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="member",
            name="last_name",
        ),
    ]
