from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy
from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex

from .gathered import GatheredPermissionsBase, gathered_permission_indexes


class ObjectAccess(GatheredPermissionsBase):
    class Meta:
        verbose_name = pgettext_lazy('pxd_legate', 'Object access')
        verbose_name_plural = pgettext_lazy('pxd_legate', 'Object accesses')
        unique_together = (
            ('user', 'content_type', 'object_id'),
        )
        indexes = gathered_permission_indexes() + [
            GinIndex(
                name='%(app_label)s_%(class)s_groups',
                fields=['group_ids'], opclasses=('gin__int_ops',)
            ),
            GinIndex(
                name='%(app_label)s_%(class)s_perms',
                fields=['permission_ids'], opclasses=('gin__int_ops',)
            ),
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('pxd_legate', 'User'),
    )
    group_ids = ArrayField(
        models.IntegerField(), blank=True, default=list,
        verbose_name=pgettext_lazy('pxd_legate', 'Groups'),
    )
    permission_ids = ArrayField(
        models.IntegerField(), blank=True, default=list,
        verbose_name=pgettext_lazy('pxd_legate', 'Permissions'),
    )
