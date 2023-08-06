from typing import List, Sequence

from pxd_combinable_groups.services import permissions_collector

from ..models import ObjectAccess
from ..utils import upset


def gather_object_accesses(
    accesses: Sequence[ObjectAccess],
    update: bool = True,
) -> List[ObjectAccess]:
    collected = permissions_collector.collect_sets(
        access.group_ids
        for access in accesses
    )
    accesses = accesses if isinstance(accesses, list) else list(accesses)

    for i, permissions in enumerate(collected):
        accesses[i].gathered_permission_ids = list(upset(
            permissions, accesses[i].permission_ids
        ))

    if update:
        ObjectAccess.objects.bulk_update(accesses, fields=(
            'gathered_permission_ids',
        ))

    return accesses
