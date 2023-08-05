from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('TreeConfig',)


class TreeConfig(AppConfig):
    name = 'pxd_tree'
    verbose_name = pgettext_lazy('pxd_tree', 'Tree')
