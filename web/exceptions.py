class UserException(Exception):
    """ General user exception. """


class SchemaError(UserException):
    """ General schema error. """


class TypeSchemaError(SchemaError):
    """ Raised if there is invalid type in data dictionary. """


class RequiredSchemaError(SchemaError):
    """ Raised if there is no required data in dictionary. """


class MinLengthSchemaError(SchemaError):
    """ Raised if length of string in data is less then minimum. """


class MaxLengthSchemaError(SchemaError):
    """ Raised if length of string in data is greater then maximum. """


class MinimumSchemaError(SchemaError):
    """ Raised if value in data is less then minimum. """


class MaximumSchemaError(SchemaError):
    """ Raised if value in data is greater then maximum. """