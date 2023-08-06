from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from pxd_combinable_groups.utils import get_permission_model

from .services import gatherer
from .models import ObjectAccess
from .conf import settings


Permission = get_permission_model()


@admin.register(ObjectAccess)
class ObjectAccessAdmin(admin.ModelAdmin):
    list_display = 'id', 'content_type', 'object_id', 'user'
    list_select_related = 'user', 'content_type',
    autocomplete_fields = 'user',
    list_filter = 'content_type',
    search_fields = (
        'content_type__app_label', 'content_type__model',
        'user__username', 'object_id',
    )

    def save_model(self, request, obj, form, change):
        result = super().save_model(request, obj, form, change)

        gatherer.gather_object_accesses((obj,))

        return result


class OnlyViewMixin:
    has_delete_permission = lambda *a: False
    has_change_permission = lambda *a: False
    has_add_permission = lambda *a: False


if settings.ADMIN_REGISTER_PERMISSION and not admin.site.is_registered(Permission):
    @admin.register(Permission)
    class PermissionAdmin(OnlyViewMixin, admin.ModelAdmin):
        list_display = '__str__', 'id', 'codename', 'content_type',
        list_select_related = 'content_type',
        list_filter = 'content_type',
        search_fields = (
            'content_type__app_label', 'content_type__model',
            'codename',
        )


if settings.ADMIN_REGISTER_CONTENT_TYPE and not admin.site.is_registered(ContentType):
    @admin.register(ContentType)
    class ContentTypeAdmin(OnlyViewMixin, admin.ModelAdmin):
        list_display = '__str__', 'id', 'app_label', 'model',
        list_filter = 'app_label',
