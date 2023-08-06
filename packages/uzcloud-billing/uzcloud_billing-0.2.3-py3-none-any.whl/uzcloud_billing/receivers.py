from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from uzcloud_billing.models import BillingAccount

User = get_user_model()


@receiver(post_save, sender=User)
def create_billing_account(sender: User, instance: User, created, **kwargs):
    if created:
        BillingAccount.objects.create(user=instance)
