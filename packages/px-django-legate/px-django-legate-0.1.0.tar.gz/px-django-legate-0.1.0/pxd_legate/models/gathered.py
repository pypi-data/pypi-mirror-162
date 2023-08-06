from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import pgettext_lazy
from django.db import models


class GatheredPermissionsBase(models.Model):
    class Meta:
        abstract = True

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('pxd_legate', 'Object: Content type'),
    )
    object_id = models.PositiveIntegerField(
        verbose_name=pgettext_lazy('pxd_legate', 'Object: Identifier'),
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    gathered_permission_ids = ArrayField(
        models.IntegerField(), blank=True, default=list,
        verbose_name=pgettext_lazy('pxd_legate', 'Gathered permissions'),
    )


def gathered_permission_indexes(name: str = '%(app_label)s_%(class)s'):
    return [
        models.Index(fields=['content_type', 'object_id']),
        GinIndex(
            name=name + '_gth',
            fields=['gathered_permission_ids'], opclasses=('gin__int_ops',)
        )
    ]
