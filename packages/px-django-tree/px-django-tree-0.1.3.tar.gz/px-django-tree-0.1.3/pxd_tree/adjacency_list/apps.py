from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('AdjacencyListTreeConfig',)


class AdjacencyListTreeConfig(AppConfig):
    name = 'pxd_tree.adjacency_list'
    label = 'pxd_tree_adjacency_list'
    verbose_name = pgettext_lazy('pxd_tree', 'Adjacency list tree')
