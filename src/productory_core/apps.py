from django.apps import AppConfig


class ProductoryCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "productory_core"
    verbose_name = "Productory Core"

    def ready(self):
        from productory_core import audit_signals  # noqa: F401
