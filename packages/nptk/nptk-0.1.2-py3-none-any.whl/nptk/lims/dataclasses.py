from typing import Any, List, Tuple

from dataclasses import dataclass


@dataclass
class Query:

    query_str: str
    filters: list[tuple[str, Any]]
    return_name: str
