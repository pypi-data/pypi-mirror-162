class SQLLoadException(Exception):
    """Raised when there is a problem loading SQL content from a file or directory."""

    pass


class SQLParseException(Exception):
    """Raised when there was a problem parsing the raw-sql comment annotations in SQL"""

    pass
