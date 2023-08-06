from enum import Enum


class Types(Enum):
    String = "String"
    Integer = "Integer"  # 32 bit
    Long = "Long"  # 64 bit
    Double = "Double"  # (15-16 digits)
    # Decimal = "Decimal"  # (28-29 significant digits)
    Boolean = "Boolean"
    Date = "Date"
    # Timestamp = "Timestamp"
    Object = "Object"
    Array = "Array"
    Buffer = "Buffer"
    # Undefined = "Undefined"
    Null = "Null"
