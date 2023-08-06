import logging
from pathlib import Path
from typing import Union

from pure_sql.exceptions import SQLLoadException
from pure_sql.query_loader import QueryLoader

log = logging.getLogger(__name__)


def from_str(sql: str):
    """Load queries from a SQL string."""
    query_loader = QueryLoader()
    query_data = query_loader.load_query_data_from_sql(sql)
    return query_data


def from_path(sql_path: Union[str, Path]):
    """Load queries from a `.sql` file, or directory of `.sql` files."""
    path = Path(sql_path)

    if not path.exists():
        raise SQLLoadException(f"File does not exist: {path}")

    query_loader = QueryLoader()

    if path.is_file():
        query_data = query_loader.load_query_data_from_file(path)
        return query_data
    elif path.is_dir():
        query_data_tree = query_loader.load_query_data_from_dir_path(path)
        return query_data_tree
    else:  # pragma: no cover
        raise SQLLoadException(
            f"The sql_path must be a directory or file, got {sql_path}"
        )
