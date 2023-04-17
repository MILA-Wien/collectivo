"""Models of the lotzapp extension."""
import requests
from django.contrib.auth import get_user_model
from django.db import models

from collectivo.utils.exceptions import APIException
from collectivo.utils.models import SingleInstance

User = get_user_model()


class LotzappSettings(SingleInstance, models.Model):
    """Settings for the lotzapp extension."""

    lotzapp_url = models.URLField(max_length=255)
    lotzapp_user = models.CharField(max_length=255)
    lotzapp_pass = models.CharField(max_length=255)
    zahlungsmethode_sepa = models.IntegerField(null=True)
    zahlungsmethode_transfer = models.IntegerField(null=True)
    adressgruppe = models.IntegerField(null=True)


class LotzappAddress(models.Model):
    """A connector between collectivo users and lotzapp addresses."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lotzapp",
    )

    lotzapp_id = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        """Return user name."""
        return str(self.user)

    def sync(self):
        """Sync the invoice with lotzapp."""

        settings = LotzappSettings.object(check_valid=True)
        address_endpoint = settings.lotzapp_url + "adressen/"
        data = {}  # TODO Address payload

        if self.lotzapp_id == "":
            response = requests.post(
                address_endpoint,
                auth=(settings.lotzapp_user, settings.lotzapp_pass),
                data=data,
                timeout=10,
            )
            self.lotzapp_id = response.json()["ID"]
            self.save()

        else:
            response = requests.put(
                address_endpoint + self.lotzapp_id + "/",
                auth=(settings.lotzapp_user, settings.lotzapp_pass),
                data=data,
                timeout=10,
            )

        if response.status_code not in (200, 201):
            raise APIException(
                f"Lotzapp address sync failed with {response.status_code}."
            )


class LotzappInvoice(models.Model):
    """A connector between collectivo invoices and lotzapp invoices."""

    invoice = models.OneToOneField(
        "payments.Invoice",
        on_delete=models.CASCADE,
        related_name="lotzapp",
    )
    lotzapp_id = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        """Return the lotzapp id."""
        return self.lotzapp_id

    def sync(self):
        """Sync the invoice with lotzapp."""
        settings = LotzappSettings.object(check_valid=True)
        ar_endpoint = settings.lotzapp_url + "ar/"

        if self.lotzapp_id == "":
            # Get the address ID from lotzapp
            try:
                address_id = self.invoice.payment_from.lotzapp.lotzapp_id
            except self.invoice.payment_from.lotzapp.RelatedObjectDoesNotExist:
                raise APIException(
                    "Lotzapp address does not exist. Please sync addresses."
                )

            # Create the invoice in lotzapp
            data = {
                # TODO: Adresse == User
                "positionen": [
                    {
                        "adresse": address_id,
                        "artikel": item.type.name,  # TODO: Category
                        "menge": item.amount,
                        "preis": item.price,
                    }
                    for item in self.invoice.items.all()
                ]
            }
            response = requests.post(
                ar_endpoint,
                auth=(settings.lotzapp_user, settings.lotzapp_pass),
                data=data,
                timeout=10,
            )
            if response.status_code != 201:
                raise APIException("Lotzapp invoice creation failed.")
            self.lotzapp_id = response.json()["ID"]
            self.save()

        else:
            # TODO: Get the status of the invoice from lotzapp
            pass

        if response.status_code not in (200, 201):
            raise APIException(
                f"Lotzapp address sync failed with {response.status_code}."
            )
