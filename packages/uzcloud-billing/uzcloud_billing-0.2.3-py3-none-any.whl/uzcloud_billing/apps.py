from django.apps import AppConfig


class UzcloudBillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uzcloud_billing"

    def ready(self) -> None:
        from uzcloud_billing import receivers
