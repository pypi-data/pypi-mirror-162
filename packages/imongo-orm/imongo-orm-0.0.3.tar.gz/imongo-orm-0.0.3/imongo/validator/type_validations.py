import datetime

from imongo.types import Types

TYPE_VALIDATIONS = {
    Types.String: lambda value: isinstance(value, str),
    Types.Integer: lambda value: isinstance(value, int),
    Types.Long: lambda value: isinstance(value, int),
    Types.Double: lambda value: isinstance(value, float),
    # Types.Decimal: lambda value: isinstance(value, float),
    Types.Boolean: lambda value: isinstance(value, bool),
    Types.Date: lambda value: isinstance(value, datetime.datetime),
    # Types.Timestamp: lambda value: isinstance(value, datetime.datetime),
    Types.Object: lambda value: isinstance(value, dict),
    Types.Array: lambda value: isinstance(value, list),
    Types.Buffer: lambda value: isinstance(value, bytes),
    # Types.Undefined: lambda value: value is None,
    Types.Null: lambda value: value is None,
}
