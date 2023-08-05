from dataclasses import dataclass
from django.contrib.postgres.fields import ArrayField
from typing import Dict, List, Optional, Sequence, Tuple, Union
from django.db import models

from ..db import ALAncestors, ALDescendants


__all__ = 'FieldsConfig', 'TreeCollector',

IDS = Union[Sequence[int], models.QuerySet]


@dataclass
class FieldsConfig:
    id: str
    parent: str
    parent_id: str


def IntArray():
    return ArrayField(models.IntegerField())


class TreeCollector:
    fields: FieldsConfig
    queryset: models.QuerySet
    identifier_field = '_q_pk'

    def __init__(self, fields: FieldsConfig, queryset: models.QuerySet):
        self.fields = fields
        self.queryset = queryset

    def get_queryset(self):
        return self.queryset

    def ids_q(self, ids: IDS):
        f = self.fields
        filter_q = models.Q()
        whens = []

        # HACK!
        # Ugliest thing I've ever done)
        # With django orm you cant just select from some array of ids.
        # So that's why we're searching for values in parent and child id
        # fields id and for those that exists - building a tree.
        for field in (f.id, f.parent_id):
            # TODO: Analyze whether the `any` postgres function is better than
            # `in` operator in this case or not.
            # Since IDS could be a queryset - think it will be better to
            # use `in`.
            # cmp = {field: models.Func(
            #     models.Value(ids, output_field=IntArray()), function='any'
            # )}
            cmp = {f'{field}__in': ids}

            whens.append(models.When(models.Q(**cmp), then=models.F(field)))
            filter_q |= models.Q(**cmp)

        return (
            self.get_queryset()
            .filter(filter_q)
            .annotate(**{self.identifier_field: models.Case(*whens)})
            # TODO: There should not be any case when there will be a
            # situation with nulled identifier. But shit happens so
            # this will stay commented)
            # .exclude(**{f'{self.identifier_field}__isnull': True})
            .order_by(self.identifier_field)
            .distinct(self.identifier_field)
        )

    def get_ancestors(
        self, ids: IDS,
    ) -> List[Tuple[int, List[int]]]:
        f = self.fields

        return (
            self.ids_q(ids)
            .annotate(
                _ancestors_list=ALAncestors(
                    models.F(self.identifier_field),
                    models.Value(self.queryset.model._meta.db_table),
                    models.Value(f.parent_id),
                    models.Value(f.id),
                    output_field=IntArray(),
                )
            )
            .values_list(self.identifier_field, '_ancestors_list')
        )

    def get_descendants(
        self, ids: IDS,
    ) -> List[Tuple[int, List[int]]]:
        f = self.fields

        return (
            self.ids_q(ids)
            .annotate(
                _descendants_list=ALDescendants(
                    models.F(self.identifier_field),
                    models.Value(self.queryset.model._meta.db_table),
                    models.Value(f.parent_id),
                    models.Value(f.id),
                    output_field=IntArray(),
                )
            )
            .values_list(self.identifier_field, '_descendants_list')
        )
