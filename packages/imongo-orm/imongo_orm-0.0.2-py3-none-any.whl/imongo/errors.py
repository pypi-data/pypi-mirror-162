class SchemaMismatchError(Exception):
    pass


class SchemaDataTypeMismatchError(SchemaMismatchError):
    pass


class SchemaImmutableOverwriteError(SchemaMismatchError):
    pass
