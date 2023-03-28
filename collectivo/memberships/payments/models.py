"""Models of the memberships_payments extension."""
from django.db import models, transaction
from django.db.models import signals

from collectivo.memberships.models import Membership
from collectivo.payments.models import Payment, Subscription


class MembershipPayments(models.Model):
    """Mediator between a membership and payments."""

    membership = models.OneToOneField(
        "memberships.Membership",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="payments",
    )
    shares_signed = models.IntegerField(default=0)
    shares_payments = models.ManyToManyField(
        "payments.Payment", related_name="membership_shares", blank=True
    )
    fees_subscription = models.ForeignKey(
        "payments.Subscription",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="membership_fees",
    )

    def delete(self):
        """Delete subscription if membership is deleted."""
        with transaction.atomic():
            if self.fees_subscription is not None:
                self.fees_subscription.delete()
            super().delete()

    def create_payment_for_shares(self):
        """Create payment for shares."""
        mtype = self.membership.type
        if mtype.has_shares:
            shares_diff = self.membership.shares_signed - self.shares_signed
            self.shares_signed = self.membership.shares_signed

            if shares_diff < 0:
                raise NotImplementedError("Cannot remove shares")

            if shares_diff > 0:
                payment = Payment.objects.create(
                    name="Shares",
                    description=f"{shares_diff} shares for {mtype.name}",
                    payer=self.membership.user.payment_profile,
                    amount=shares_diff * mtype.shares_amount_per_share,
                    status="pending",
                    currency=mtype.currency,
                    date_due=self.membership.date_started,
                )
                return payment

    def create_subscription_for_fees(self):
        """Create subscription for membership fees."""

        if self.membership.type.has_fees:
            if self.fees_subscription is None:
                sub = Subscription()
            else:
                sub = self.fees_subscription

            sub.name = "Fees"
            sub.description = (
                f"Membership fees for {self.membership.type.name}"
            )
            sub.amount = self.membership.type.fees_amount_standard
            sub.payer = self.membership.user.payment_profile
            sub.starting_date = self.membership.date_started
            sub.repeat_each = self.membership.type.fees_repeat_each
            sub.repeat_unit = self.membership.type.fees_repeat_unit
            sub.save()
            self.fees_subscription = sub
            super().save()

    def save(self, *args, **kwargs):
        """Create payments."""
        with transaction.atomic():
            payment = self.create_payment_for_shares()
            super().save(*args, **kwargs)
            self.create_subscription_for_fees()
            if payment is not None:
                self.shares_payments.add(payment)
                super().save()


def payments_to_membership(sender, instance, **kwargs):
    """Update membership from payment."""

    # Only update if payment has been changed to successfull
    if instance.status != "success":
        return
    if instance.pk:
        old = Payment.objects.get(pk=instance.pk)
        if old.status == "success":
            return

    # Write paid shares to membership
    if instance.membership_shares.exists():
        membership = instance.membership_shares.first().membership
        shares_paid = int(
            instance.amount / membership.type.shares_amount_per_share
        )
        membership.shares_paid += shares_paid
        membership.save()


signals.pre_save.connect(
    payments_to_membership,
    sender=Payment,
    dispatch_uid="payments_to_membership",
    weak=False,
)


def membership_to_payments(sender, instance, created, **kwargs):
    """Update membership payments when membership changes."""
    if created:
        connector = MembershipPayments.objects.create(membership=instance)
    else:
        connector = instance.payments
    connector.save()


signals.post_save.connect(
    membership_to_payments,
    sender=Membership,
    dispatch_uid="membership_to_payments",
    weak=False,
)
