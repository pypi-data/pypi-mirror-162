from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Set, Tuple, Type, TypeVar
from functools import reduce

from django.db import models

from .checker import RawCheckCMP, Checker, Checkable, CheckCMP
from ..utils import make_random_code
from ..exceptions import NoCheckers

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser as User


C = TypeVar('C', bound=Checker)
REGISTRY_ANNOTATION_FIELD_TEMPLATE = '_registered_permissions_{name}_exists'


ALL_CMP = RawCheckCMP(
    lambda fields: reduce(
        lambda acc, x: acc & models.Q(**{x: True}), fields, models.Q()
    ),
    all,
)
ANY_CMP = RawCheckCMP(
    lambda fields: reduce(
        lambda acc, x: acc | models.Q(**{x: True}), fields, models.Q()
    ),
    any,
)


class Registry(Checkable):
    index: Set[Checker]
    map: Dict[Type[models.Model], List[Checker]]
    cmp: CheckCMP = ANY_CMP

    def __init__(
        self,
        cmp: Optional[CheckCMP] = None,
        raise_noncheckable: bool = False,
    ):
        self.index = set()
        self.map = {}
        self.raise_noncheckable = raise_noncheckable
        self.cmp = cmp if cmp is not None else self.cmp

    def has(self, checker: C) -> bool:
        return checker in self.index

    def add(self, checker: C) -> C:
        assert not self.has(checker), 'Checker already registered.'

        self.index.add(checker)
        model = checker.model
        self.map[model] = self.map.get(model, [])
        self.map[model].append(checker)

        return checker

    def remove(self, checker: C) -> bool:
        if not self.has(checker):
            return False

        self.index.remove(checker)
        self.map[checker.model].remove(checker)

        return True

    def _make_annotation_field_name(self, name: str) -> str:
        return REGISTRY_ANNOTATION_FIELD_TEMPLATE.format(name=name)

    def _get_checkers(self, model: Type[models.Model]):
        return self.map.get(model, [])

    def with_annotation(
        self,
        queryset: models.QuerySet,
        user: 'User',
        permission_ids: Optional[Sequence[int]] = None,
        cmp: Optional[CheckCMP] = None,
        annotation_field_name: Optional[str] = None,
        raise_noncheckable: Optional[bool] = None,
    ) -> Tuple[str, models.QuerySet]:
        raise_noncheckable = (
            raise_noncheckable if raise_noncheckable is not None
            else self.raise_noncheckable
        )
        annotation_field_name = (
            annotation_field_name
            or
            self._make_annotation_field_name(make_random_code(6))
        )
        model = queryset.model
        checkers = self._get_checkers(model)

        if len(checkers) == 0:
            if raise_noncheckable:
                raise NoCheckers(f'No checkers for model "{model}".')

            return annotation_field_name, queryset.annotate(**{
                annotation_field_name: models.Value(True)
            })

        fields = []

        for checker in checkers:
            field, queryset = checker.with_annotation(
                queryset, user, permission_ids=permission_ids
            )
            fields.append(field)

        return annotation_field_name, queryset.annotate(**{
            annotation_field_name: models.ExpressionWrapper(
                (cmp or self.cmp).cmp_Q(fields),
                output_field=models.BooleanField(),
            )
        })

    def for_object(
        self,
        obj: models.Model,
        user: 'User',
        permission_ids: Sequence[int],
        cmp: Optional[CheckCMP] = None,
        raise_noncheckable: Optional[bool] = None,
    ) -> bool:
        raise_noncheckable = (
            raise_noncheckable if raise_noncheckable is not None
            else self.raise_noncheckable
        )
        model = obj.__class__
        checkers = self._get_checkers(model)
        if len(checkers) == 0:
            if raise_noncheckable:
                raise NoCheckers(f'No checkers for model "{model}".')

            return True

        return (cmp or self.cmp).cmp(
            checker.for_object(obj, user, permission_ids=permission_ids)
            for checker in checkers
        )

    def for_queryset(
        self,
        queryset: models.QuerySet,
        user: 'User',
        permission_ids: Optional[Sequence[int]] = None,
        cmp: Optional[CheckCMP] = None,
        annotation_field_name: Optional[str] = None,
        raise_noncheckable: Optional[bool] = None,
    ) -> models.QuerySet:
        name, q = self.with_annotation(
            queryset, user,
            permission_ids=permission_ids, cmp=cmp,
            annotation_field_name=annotation_field_name,
            raise_noncheckable=raise_noncheckable,
        )

        return q.filter(**{name: True})
