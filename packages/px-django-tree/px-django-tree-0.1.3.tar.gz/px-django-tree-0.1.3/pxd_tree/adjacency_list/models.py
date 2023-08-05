from django.db import models
from django.utils.translation import pgettext_lazy


__all__ = 'Tree',


class Tree(models.Model):
    class Meta:
        abstract = True

    parent = models.ForeignKey(
        'self',
        verbose_name=pgettext_lazy('pxd_tree', 'Parent entity'),
        on_delete=models.SET_NULL, null=True, blank=True, default=None,
        db_index=True
    )
