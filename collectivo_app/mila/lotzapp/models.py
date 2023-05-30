"""Models of the lotzapp extension."""
import logging
from datetime import datetime

import requests
from celery import chord
from django.contrib.auth import get_user_model
from django.db import models

from collectivo.payments.models import Invoice
from collectivo.utils.exceptions import APIException
from collectivo.utils.models import SingleInstance

logger = logging.getLogger(__name__)
User = get_user_model()


def check_response(response):
    """Throw error if lotzapp returns an invalid response."""
    if response.status_code not in (200, 201, 204):
        raise_sync_error(response)


def raise_sync_error(response):
    """Raise an exception with the error message from lotzapp."""
    raise APIException(
        f"Lotzapp sync failed with {response.status_code}:"
        f" {response.text if hasattr(response, 'text') else ''}"
    )


def create_item_name(item):
    """Create a name for a lotzapp invoice item."""
    name = str(item.type)
    name.replace("Shares", "Genossenschaftsanteile")
    name.replace("Fees", "Mitgliedsbeitrag")
    return name


class LotzappMixin:
    """Mixin for lotzapp models to create and update objects."""

    def create_new(self, address_endpoint, auth, data):
        """Create a new object."""
        response = requests.post(
            address_endpoint,
            auth=auth,
            json=data,
            timeout=10,
        )
        check_response(response)
        try:
            res = response.json()
            if "ID" in res and res["ID"]:
                self.lotzapp_id = str(response.json()["ID"])
                self.save()
        except requests.exceptions.JSONDecodeError:
            raise_sync_error(response)

    def get(self, endpoint, auth):
        """Try to get existing object."""
        return requests.get(
            endpoint + str(self.lotzapp_id) + "/",
            auth=auth,
            timeout=10,
        )

    def update_existing(self, endpoint, auth, data):
        """Update an existing object."""
        get_response = self.get(endpoint, auth)
        check_response(get_response)

        # If ID exists, update object
        if get_response.status_code != 204:
            put_response = requests.put(
                endpoint + str(self.lotzapp_id) + "/",
                auth=auth,
                json=data,
                timeout=10,
            )
            check_response(put_response)

        # If ID does not exist, create new object
        else:
            self.create_new(endpoint, auth, data)

        return get_response


class LotzappSettings(SingleInstance, models.Model):
    """Settings for the lotzapp extension."""

    lotzapp_url = models.URLField(max_length=255)
    lotzapp_user = models.CharField(max_length=255)
    lotzapp_pass = models.CharField(max_length=255)
    zahlungsmethode_sepa = models.IntegerField(null=True)
    zahlungsmethode_transfer = models.IntegerField(null=True)
    adressgruppe_eg = models.IntegerField(null=True)
    adressgruppe_verein = models.IntegerField(null=True)


class LotzappSync(models.Model):
    """A documentation of a sync action."""

    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=255,
        default="pending",
        choices=(
            ("pending", "pending"),
            ("success", "success"),
            ("failure", "failure"),
        ),
    )
    type = models.CharField(
        max_length=255,
        choices=(
            ("invoice", "Rechnungen & zugehörige Adressen"),
            ("address", "Adressen"),
        ),
    )
    status_message = models.TextField()

    def save(self, *args, **kwargs):
        """Save the object and call sync for new entry."""
        new = self.pk is None
        super().save(*args, **kwargs)
        if new:
            self.sync()

    def sync(self):
        """Synchronize lotzapp with collectivo."""
        from .tasks import (
            sync_lotzapp_end,
            sync_lotzapp_invoice,
            sync_lotzapp_user,
        )

        if self.type == "invoice":
            tasks = [sync_lotzapp_invoice.s(i) for i in Invoice.objects.all()]
        else:
            tasks = [sync_lotzapp_user.s(u) for u in User.objects.all()]
        chord(tasks)(sync_lotzapp_end.s(self))


class LotzappAddress(LotzappMixin, models.Model):
    """A connector between collectivo users and lotzapp addresses."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lotzapp",
    )

    lotzapp_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """Return user name."""
        return str(self.user)

    def sync(self):
        """Sync the invoice with lotzapp."""

        user = self.user
        profile = self.user.profile
        payments = self.user.payment_profile
        settings = LotzappSettings.object(check_valid=True)
        auth = (settings.lotzapp_user, settings.lotzapp_pass)
        address = (
            f"{profile.address_street} {profile.address_number} "
            f"{profile.address_stair} {profile.address_door}"
        )
        address_endpoint = settings.lotzapp_url + "adressen/"
        data = {
            "name2": user.first_name,
            "name": user.last_name,
            "typ": "0" if profile.person_type == "legal" else "1",
            "anschrift": address,
            "plz": profile.address_postcode,
            "ort": profile.address_city,
            "bankeinzug": "1" if payments.payment_method == "sepa" else "0",
            "mail": [{"email": user.email}],
            "bankverbindungen": [{"IBAN": payments.bank_account_iban}],
        }

        if self.lotzapp_id == "":
            self.create_new(address_endpoint, auth, data)
        else:
            self.update_existing(address_endpoint, auth, data)


class LotzappInvoice(LotzappMixin, models.Model):
    """A connector between collectivo invoices and lotzapp invoices."""

    invoice = models.OneToOneField(
        "payments.Invoice",
        on_delete=models.CASCADE,
        related_name="lotzapp",
    )
    lotzapp_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """Return the lotzapp id."""
        return self.lotzapp_id

    def prepare_invoice_data(self):
        """Create payload for invoice."""

        settings = LotzappSettings.object(check_valid=True)

        # Sync address
        try:
            lotzapp_address = self.invoice.payment_from.user.lotzapp
        except LotzappAddress.DoesNotExist:
            lotzapp_address = LotzappAddress.objects.create(
                user=self.invoice.payment_from.user
            )
        lotzapp_address.sync()
        lotzapp_address.refresh_from_db()

        # Prepare invoice data for lotzapp
        zahlungsmethode = (
            settings.zahlungsmethode_sepa
            if self.invoice.payment_from.user.payment_profile.payment_method
            == "sepa"
            else settings.zahlungsmethode_transfer
        )

        # Type conversion
        zahlungsmethode = int(zahlungsmethode) if zahlungsmethode else None
        adresse = lotzapp_address.lotzapp_id
        adresse = int(adresse) if adresse else None

        # Prepare payload
        return {
            "datum": self.invoice.date.strftime("%Y-%m-%d"),
            "adresse": int(lotzapp_address.lotzapp_id),
            "zahlungsmethode": zahlungsmethode,
            "positionen": [
                {
                    "name": create_item_name(item),
                    "wert": str(item.amount),
                    "einheit": "mal",
                    "netto": str(item.price),
                }
                for item in self.invoice.items.all()
            ],
        }

    def sync(self):
        """Sync the invoice with lotzapp."""
        settings = LotzappSettings.object(check_valid=True)
        auth = (settings.lotzapp_user, settings.lotzapp_pass)
        ar_endpoint = settings.lotzapp_url + "ar/"

        # Create invoice in lotzapp there is no id
        if self.lotzapp_id == "":
            data = self.prepare_invoice_data()
            self.create_new(ar_endpoint, auth, data)

        elif self.invoice.date_paid is None:
            response = self.get(ar_endpoint, auth)

            # Create invoice in lotzapp if it does not exist
            if response.status_code == 204:
                data = self.prepare_invoice_data()
                self.create_new(ar_endpoint, auth, data)

            # If it exists, check if invoice is paid in lotzapp
            else:
                try:
                    res = response.json()[0]
                    date_paid = res.get("bezahlt", "0000-00-00")
                    if date_paid != "0000-00-00":
                        self.invoice.status = "paid"
                        self.invoice.date_paid = datetime.strptime(
                            date_paid, "%Y-%m-%d"
                        ).date()
                        self.invoice.save()
                except requests.exceptions.JSONDecodeError:
                    logger.warning("Could not decode lotzapp response.")
