from django.core.exceptions import PermissionDenied
from wagtail import hooks


@hooks.register("before_delete_page")
def guard_page_delete(request, page):
    if not request.user.is_superuser:
        raise PermissionDenied("Only administrators can delete pages.")


@hooks.register("before_bulk_action")
def guard_bulk_delete(request, action_type, objects, action):
    if action_type == "delete" and not request.user.is_superuser:
        raise PermissionDenied("Only administrators can delete content.")
