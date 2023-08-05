from .services.tree_collector import FieldsConfig


__all__ = 'FieldsConfig', 'DEFAULT_FIELDS_CONFIG',

DEFAULT_FIELDS_CONFIG = FieldsConfig(
    id='id', parent='parent', parent_id='parent_id'
)
