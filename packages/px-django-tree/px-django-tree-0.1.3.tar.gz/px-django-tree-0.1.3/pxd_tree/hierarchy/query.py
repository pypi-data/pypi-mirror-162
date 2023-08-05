from typing import Optional, Sequence, TypeVar
from enum import Enum
from functools import reduce
from django.db.models import (
    Q, Case, When, Func, Value, BooleanField, F, QuerySet,
    IntegerField, TextField, Exists, OuterRef, Subquery, CharField
)
from django.db.models.functions import Cast
from pxd_postgres.ltree.fields import LtreeField
from pxd_tree.adjacency_list import TreeQuerySet as Base
from pxd_postgres.ltree import (
    LtreeIntField, LtreeConcatFunc, LtreeValue, LtreeSubpathFunc
)

from .const import FieldsConfig, DEFAULT_FIELDS_CONFIG

__all__ = (
    'rough_valid_path',
    'descendants_list',
    'ancestors_list',
    'roots_list',
    'TreeQuerySet',
)

QT = TypeVar('QT', bound='TreeQuerySet')
NQS = Optional[QT]



def lt_cast(f):
    return Cast(Cast(f, output_field=TextField()), output_field=LtreeIntField())


def lt_id():
    return lt_cast(F('id'))


class PathIssues(str, Enum):
    VALID: str = 'VALID'

    INVALID: str = 'INVALID'
    EMPTY_PATH: str = 'EMPTY_PATH'
    WRONG_PARENT_PATH: str = 'WRONG_PARENT_PATH'


def rough_valid_path(
    qs: QuerySet,
    validity_field: str = 'is_roughly_valid_element',
    validity_state_field: str = 'roughly_valid_state',
    id_field: str = DEFAULT_FIELDS_CONFIG.id,
    parent_id_field: str = DEFAULT_FIELDS_CONFIG.parent_id,
    parent_field: str = DEFAULT_FIELDS_CONFIG.parent,
    path_field: str = DEFAULT_FIELDS_CONFIG.path
) -> QuerySet:
    return (
        qs
        .annotate(**{
            validity_state_field: Case(
                When(
                    Q(**{f'{path_field}__exact': ''}),
                    then=Value(PathIssues.EMPTY_PATH)
                ),
                When(
                    Q(parent_id__isnull=False) & ~Q(path__exact=LtreeConcatFunc(F('parent__path'), lt_id())),
                    then=Value(PathIssues.WRONG_PARENT_PATH)
                ),
                When(
                    Q(**{
                        f'{parent_id_field}__isnull': True,
                        f'{path_field}__exact': Cast(
                            Cast(id_field, output_field=TextField()),
                            output_field=LtreeIntField()
                        ),
                    }),
                    then=Value(PathIssues.VALID)
                ),
                When(
                    (
                        Q(**{
                            f'{parent_id_field}__isnull': False,
                            f'{parent_field}__{path_field}__ancestor': F(path_field),

                        })
                        &
                        ~Q(**{
                            f'{parent_field}__{path_field}__depth': F(f'{path_field}__depth'),
                        })
                    ),
                    then=Value(PathIssues.VALID)
                ),
                default=Value(PathIssues.INVALID),
                output_field=CharField()
            )
        })
        .annotate(**{
            validity_field: Case(
                When(
                    Q(**{validity_state_field: PathIssues.VALID}),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField(),
            )
        })
    )


def descendants_list(
    qs: QuerySet,
    within: QuerySet,
    path_field: str = DEFAULT_FIELDS_CONFIG.path
) -> Q:
    return (
        within
        .annotate(_is_descendant=Exists(Subquery(
            qs.filter(**{f'{path_field}__ancestor': OuterRef(path_field)})
        )))
        .filter(_is_descendant=True)
    )

def ancestors_list(
    qs: QuerySet,
    within: QuerySet,
    path_field: str = DEFAULT_FIELDS_CONFIG.path
) -> Q:
    return (
        within
        .annotate(_is_ancestor=Exists(Subquery(
            qs.filter(**{f'{path_field}__descendant': OuterRef(path_field)})
        )))
        .filter(_is_ancestor=True)
    )


def roots_list(
    qs: QuerySet,
    within: QuerySet,
    path_field: str = DEFAULT_FIELDS_CONFIG.path
) -> Q:
    return ancestors_list(qs, within, path_field=path_field).filter(**{
        f'{path_field}__depth': 1,
    })


class TreeQuerySet(QuerySet):
    fields: FieldsConfig = DEFAULT_FIELDS_CONFIG

    def _get_tree_within(self: QT, within: NQS = None) -> QT:
        return (
            self.model.objects.using(self._db).all()
            if within is None
            else within
        )

    def siblings(self: QT, within: NQS = None) -> QT:
        """Lookups for a nodes siblings."""
        within = self._get_tree_within(within)
        f = self.fields

        return (
            within
            .filter(**{f'{f.id}__in': self.values(f.parent_id)})
            .exclude(**{f'{f.id}__in': self.values(f.id)})
        )

    def descendants(self: QT, within: NQS = None) -> QT:
        return descendants_list(self, self._get_tree_within(within))

    def ancestors(self: QT, within: NQS = None) -> QT:
        return ancestors_list(self, self._get_tree_within(within))

    def roots(self: QT, within: NQS = None) -> QT:
        return roots_list(self, self._get_tree_within(within))

    def roughly_valid_elements(self, validity=True):
        return (
            rough_valid_path(self, 'is_roughly_valid_element')
            .filter(is_roughly_valid_element=validity)
        )

    def update_roughly_invalid_tree(self, within: NQS = None, repeat_times: int = 3):
        total = 0
        changed = -1
        within = self._get_tree_within(within)
        base = self.model.objects.all()

        whens: Sequence[When] = [
            When(Q(parent_id__isnull=True) & ~Q(path__exact=lt_id()), then=lt_id()),
            When(
                Q(parent_id__isnull=False) & ~Q(path__exact=LtreeConcatFunc(F('_parent_path'), lt_id())),
                then=LtreeConcatFunc(F('_parent_path'), lt_id())
            ),
        ]
        lookup = reduce(lambda acc, x: acc | x.condition, whens, Q())
        query = (
            self
            .annotate(
                _parent_path=Subquery(
                    base.filter(id=OuterRef('parent_id')).values('path')[:1]
                )
            )
            .filter(lookup)
            .order_by('_parent_path__depth', 'path__depth')
        )
        update_path = Case(*whens, default=F('path'), output_field=LtreeField())

        while repeat_times > 0 and changed != 0:
            changed = query.update(path=update_path)
            total += changed
            repeat_times -= 1

        return total

    def update_deeply_invalid_tree(self):
        raise NotImplementedError(
            'Not yet implemented. Use `.update_roughly_invalid_tree`.'
        )
