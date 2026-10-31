from django.http import HttpResponseForbidden

DELETE_METHODS = {"GET", "POST"}
BULK_DELETE_SUFFIX = "/delete/"


def is_admin_delete_request(path, method):
    if method not in DELETE_METHODS:
        return False
    if not path.startswith("/admin/"):
        return False
    if "/delete/" in path:
        return True
    return path.startswith("/admin/bulk/") and path.endswith(BULK_DELETE_SUFFIX)


class AdminDeleteGuardMiddleware:
    """Blocks every non-superuser from the admin delete routes.

    Wagtail has no distinct delete permission: add/edit implies delete, and
    published pages additionally need publish. The middleware is the
    authority; the hooks in ``cms.wagtail_hooks`` only improve the message.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if (
            user is not None
            and user.is_authenticated
            and not user.is_superuser
            and is_admin_delete_request(request.path, request.method)
        ):
            return HttpResponseForbidden("Only administrators can delete content.")

        return self.get_response(request)
