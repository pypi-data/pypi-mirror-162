from typing import Optional, TypeVar

from .const import FieldsConfig, DEFAULT_FIELDS_CONFIG


__all__ = 'TreeQuerySet',


QT = TypeVar('QT', bound='TreeQuerySet')
NQS = Optional[QT]


class TreeQuerySet:
    fields: FieldsConfig = DEFAULT_FIELDS_CONFIG

    def _get_tree_within(self: QT, within: NQS = None) -> QT:
        return (
            self.model.objects.using(self._db).all()
            if within is None
            else within
        )

    def ancestors(self: QT, within: NQS = None) -> QT:
        return self._get_tree_within(within)

    def descendants(self: QT, within: NQS = None) -> QT:
        return self._get_tree_within(within)

    def children(self: QT, within: NQS = None) -> QT:
        return self._get_tree_within(within)

    def siblings(self: QT, within: NQS = None) -> QT:
        """Lookups for a nodes siblings."""
        within = self._get_tree_within(within)
        f = self.fields

        return (
            within
            .filter(**{f'{f.id}__in': self.values(f.parent_id)})
            .exclude(**{f'{f.id}__in': self.values(f.id)})
        )

    def roots(self: QT, within: NQS = None) -> QT:
        return self._get_tree_within(within)
