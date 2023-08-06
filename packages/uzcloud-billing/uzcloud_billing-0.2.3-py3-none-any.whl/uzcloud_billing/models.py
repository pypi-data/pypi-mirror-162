from django.db import models
from django.conf import settings

from uzcloud_billing.utils import generate_account_number


class BillingAccount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="billing_account",
    )
    account_number = models.CharField(
        max_length=255, default=generate_account_number, unique=True
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} - {self.account_number}"
