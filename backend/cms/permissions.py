from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.images.permissions import permission_policy as image_permission_policy
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission, Page

EDITORS = "Editors"
PAGE_CODENAMES = ("add_page", "change_page", "publish_page")
IMAGE_ACTIONS = ("add_", "change_", "choose_")


def ensure_editors_group(sender=None, **kwargs):
    root_page = Page.get_first_root_node()
    root_collection = Collection.get_first_root_node()
    if root_page is None or root_collection is None:
        return  # Wagtail's own initial data is not loaded yet

    editors, _ = Group.objects.get_or_create(name=EDITORS)

    # Normalize: the built-in group ships with extra permissions.
    GroupPagePermission.objects.filter(group=editors).delete()
    GroupCollectionPermission.objects.filter(group=editors).delete()
    editors.permissions.clear()

    editors.permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )

    for codename in PAGE_CODENAMES:
        permission = Permission.objects.get(
            content_type__app_label="wagtailcore",
            content_type__model="page",
            codename=codename,
        )
        GroupPagePermission.objects.create(
            group=editors, page=root_page, permission=permission
        )

    # Wagtail's image policy checks the swapped model's auth_model, which is
    # wagtailimages.Image, not cms.CustomImage. The custom model has no
    # choose_customimage permission.
    image_policy = image_permission_policy
    image_ct = ContentType.objects.get_for_model(image_policy.auth_model)
    image_permissions = list(
        Permission.objects.filter(
            content_type=image_ct,
            codename__in=[f"{action}image" for action in IMAGE_ACTIONS],
        )
    )
    if len(image_permissions) != len(IMAGE_ACTIONS):
        raise RuntimeError(
            f"Image permissions missing for {image_ct}: have "
            f"{[permission.codename for permission in image_permissions]}"
        )

    for permission in image_permissions:
        GroupCollectionPermission.objects.create(
            group=editors, collection=root_collection, permission=permission
        )
