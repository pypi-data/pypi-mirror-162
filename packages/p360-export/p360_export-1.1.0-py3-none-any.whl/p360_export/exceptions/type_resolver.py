class TypeGuesserException(Exception):
    pass


class DataTypeNotSupportedException(TypeGuesserException):
    pass


class InvalidDecimalTypeException(TypeGuesserException):
    pass
