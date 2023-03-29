"""Setup function of the emails extension."""
from django.contrib.auth import get_user_model

from collectivo.extensions.models import Extension
from collectivo.menus.models import MenuItem

from .apps import EmailsConfig
from .models import EmailCampaign, EmailDesign, EmailTemplate

User = get_user_model()


def setup(sender, **kwargs):
    """Initialize extension after database is ready."""

    from django.conf import settings

    extension = Extension.register(
        name=EmailsConfig.name,
        description=EmailsConfig.description,
        built_in=True,
    )

    MenuItem.register(
        name="emails",
        label="Emails",
        extension=extension,
        component="admin",
        icon_name="pi-envelope",
        requires_group="collectivo.core.admin",
        parent="admin",
        order=10,
    )

    statuses = ["success", "pending", "draft"]
    if settings.COLLECTIVO["dev.create_test_data"] is True:
        for i in range(3):
            design = EmailDesign.objects.register(
                name=f"Test design {i+1}",
                body='<html><body style="margin:0;padding:40px;word-spacing:'
                'normal;background-color:#fff;">{{content}}</body></html>',
            )
            template = EmailTemplate.objects.register(
                name=f"Test template {i+1}",
                design=design,
                subject=f"Test email {i+1}",
                body="This is a test email to {{member.first_name}}.",
            )

            # Reset campaigns that use the test template
            campaigns = EmailCampaign.objects.filter(template=template)
            for campaign in campaigns:
                campaign.delete()
            campaign = EmailCampaign.objects.create(template=template)
            campaign.status = statuses[i]
            test_users = User.objects.filter(email__startswith="test")
            campaign.recipients.set(test_users)
            campaign.save()
