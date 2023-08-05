from django.db.models import Func


__all__ = 'ArrayPosition', 'ArrayConcat',


class ArrayPosition(Func):
    function = 'ARRAY_POSITION'
    template_postgresql = "%(expressions)s[%(index)s]"

    def __init__(self, expression, index, **kw):
        self._index, = self._parse_expressions(index)
        super().__init__(expression, **kw)

    def as_sql(self, compiler, connection, **extra_context):
        extra_context['index'] = compiler.compile(self._index)
        return super().as_sql(compiler, connection, **extra_context)

    def as_postgresql(self, compiler, connection):
        return self.as_sql(compiler, connection, template=self.template_postgresql)


class ArrayConcat(Func):
    function = 'ARRAY_CONCAT'
    arg_joiner = ' || '
    template_postgresql = "[] || %(expressions)s"

    def as_postgresql(self, compiler, connection):
        return self.as_sql(compiler, connection, template=self.template_postgresql)
