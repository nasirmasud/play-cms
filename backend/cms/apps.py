from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CmsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cms"

    def ready(self):
        from . import signals  # noqa: F401  (previous-path capture + revalidation)
        from .permissions import ensure_editors_group

        post_migrate.connect(ensure_editors_group, sender=self, dispatch_uid="cms_editors")
