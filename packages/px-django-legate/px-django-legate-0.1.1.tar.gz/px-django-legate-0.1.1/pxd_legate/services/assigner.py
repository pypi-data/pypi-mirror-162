from typing import Any, Callable, List, Optional, Sequence, Tuple
from django.contrib.contenttypes.models import ContentType
from django.db import models

from wcd_device_recognizer.utils import model_bulk_get_or_create
from pxd_combinable_groups.utils import get_group_model

from ..models import ObjectAccess
from ..utils import upset
from . import gatherer


Group = get_group_model()
ObjectDefinition = Tuple[ContentType, int]


def _obj_to_raw(objects: Sequence[models.Model]):
    cache = ContentType.objects.get_for_models(*{x.__class__ for x in objects})

    return [(cache[x.__class__], x.pk) for x in objects]


def _should(*items: Sequence[Optional[Sequence[Any]]]):
    return [item is not None and len(item) != 0 for item in items]


def change_access_raw(
    user_id: int,
    object_definitions: Sequence[ObjectDefinition],
    committer: Callable[[Sequence[int], Optional[Sequence[int]]], List[int]],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    accesses = model_bulk_get_or_create(ObjectAccess, [
        ({'user_id': user_id, 'object_id': id, 'content_type': ct}, {
            'permission_ids': permission_ids or [],
            'group_ids': group_ids or [],
        })
        for ct, id in object_definitions
    ])

    for access in accesses:
        access.permission_ids = committer(access.permission_ids, permission_ids)
        access.group_ids = committer(access.group_ids, group_ids)

    # TODO: Should remove access models here if there is an empty
    # `permission_ids` and `groups_ids` attributes.

    accesses = gatherer.gather_object_accesses(accesses, update=False)

    ObjectAccess.objects.bulk_update(accesses, fields=(
        'group_ids', 'permission_ids', 'gathered_permission_ids'
    ))

    return accesses


def remove_access_raw(
    user_id: int,
    object_definitions: Sequence[ObjectDefinition],
):
    q = models.Q()

    for ct, id in object_definitions:
        q |= models.Q(object_id=id, content_type=ct)

    ObjectAccess.objects.filter(q, user_id=user_id).delete()


def ADD_COMMITTER(has: Sequence[int], add: Optional[Sequence[int]] = None) -> List[int]:
    return list(has if add is None else upset(has, add))


def add_access_raw(
    user_id: int,
    object_definitions: Sequence[ObjectDefinition],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    if not any(_should(permission_ids, group_ids)):
        return []

    return change_access_raw(
        user_id, object_definitions, ADD_COMMITTER,
        permission_ids=permission_ids, group_ids=group_ids,
    )


def WITHDRAW_COMMITTER(has: Sequence[int], withdraw: Optional[Sequence[int]] = None) -> List[int]:
    return list(has if withdraw is None else (set(has) - set(withdraw)))


def withdraw_access_raw(
    user_id: int,
    object_definitions: Sequence[ObjectDefinition],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    if not any(_should(permission_ids, group_ids)):
        return []

    return change_access_raw(
        user_id, object_definitions, WITHDRAW_COMMITTER,
        permission_ids=permission_ids, group_ids=group_ids,
    )


def SET_COMMITTER(has: Sequence[int], to_set: Optional[Sequence[int]] = None) -> List[int]:
    return list(has if to_set is None else to_set)


def set_access_raw(
    user_id: int,
    object_definitions: Sequence[ObjectDefinition],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    if (
        permission_ids is not None
        and
        group_ids is not None
        and
        len(permission_ids) == 0
        and
        len(group_ids) == 0
    ):
        remove_access_raw(user_id, object_definitions)

        return []

    return change_access_raw(
        user_id, object_definitions, SET_COMMITTER,
        permission_ids=permission_ids, group_ids=group_ids,
    )


def add_access(
    user_id: int,
    objects: Sequence[models.Model],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    return add_access_raw(
        user_id, _obj_to_raw(objects),
        permission_ids=permission_ids, group_ids=group_ids,
    )


def withdraw_access(
    user_id: int,
    objects: Sequence[models.Model],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    return withdraw_access_raw(
        user_id, _obj_to_raw(objects),
        permission_ids=permission_ids, group_ids=group_ids,
    )


def remove_access(user_id: int, objects: Sequence[models.Model]):
    return remove_access_raw(user_id, _obj_to_raw(objects))


def set_access(
    user_id: int,
    objects: Sequence[models.Model],
    permission_ids: Optional[Sequence[int]] = None,
    group_ids: Optional[Sequence[int]] = None,
) -> List[ObjectAccess]:
    return set_access_raw(
        user_id, _obj_to_raw(objects),
        permission_ids=permission_ids, group_ids=group_ids,
    )
