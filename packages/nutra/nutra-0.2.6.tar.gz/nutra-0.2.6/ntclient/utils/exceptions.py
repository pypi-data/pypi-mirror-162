"""Custom exception classes, used for bubbling up more specific errors"""


class SqlException(Exception):
    """Base class for Sql errors"""


class SqlConnectError(SqlException):
    """Typically when it can't find the *.sqlite3 file(s) on disk"""


class SqlInvalidVersionError(SqlException):
    """Raised when the expected version differs from actual, either for nt or usda DB"""


class SqlCrossDatabaseValidationError(SqlException):
    """
    Raised when data-bindings (e.g. food_id) in one db (typically nt)
    can't be found in another (typically usda)
    """
