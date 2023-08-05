from django.db.models import Func


__all__ = 'ALTrace',


class ALTrace(Func):
    function = 'PXD_AL_TRACE'


class ALDescendants(Func):
    function = 'PXD_AL_DESCENDANTS'


class ALAncestors(Func):
    function = 'PXD_AL_ANCESTORS'
