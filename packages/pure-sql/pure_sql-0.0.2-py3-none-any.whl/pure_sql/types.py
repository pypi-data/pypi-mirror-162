import inspect
from enum import Enum
from typing import Any, Dict, NamedTuple, Optional, Union

try:
    # Python 3.8 (PEP 544)
    from typing import Protocol
except ImportError:  # pragma: no cover
    from typing_extensions import Protocol  # type: ignore


class SQLOperationType(Enum):
    """Enumeration of pure-sql operation types."""

    INSERT_RETURNING = 0
    INSERT_UPDATE_DELETE = 1
    INSERT_UPDATE_DELETE_MANY = 2
    SCRIPT = 3
    SELECT = 4
    SELECT_ONE = 5
    SELECT_VALUE = 6


class QueryDatum(NamedTuple):
    query_name: str
    doc_comments: str
    operation_type: SQLOperationType
    sql: str
    record_class: Any = None
    signature: Optional[inspect.Signature] = None


# Can't make this a recursive type in terms of itself
# QueryDataTree = Dict[str, Union[QueryDatum, 'QueryDataTree']]
QueryDataTree = Dict[str, Union[QueryDatum, Dict]]
