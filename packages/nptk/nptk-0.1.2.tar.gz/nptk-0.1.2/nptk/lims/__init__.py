from typing import Dict, List, Optional, Tuple

import logging

from psycopg2 import connect, extensions, extras

from ..config import allen_config_auto_discovery
from ..exceptions import LimsError
from .dataclasses import Query
from .utils import fix_lims_path, is_windows
from .wkft import get_wkft_names, wkft_to_Query

logger = logging.getLogger(__name__)


def run_query(cursor: extensions.cursor, query: Query) -> list[str]:
    cursor.execute(query.query_str)
    filtered = []
    for row in cursor.fetchall():
        for (key, value) in query.filters:
            if row[key] != value:
                break
        else:
            filtered.append(row[query.return_name])
    return filtered


def _init_cursor(db_uri: str) -> extensions.cursor:
    logger.info("Connecting to database uri: %s..." % db_uri)
    con = connect(db_uri)
    con.set_session(readonly=True, autocommit=True)
    return con.cursor(
        cursor_factory=extras.RealDictCursor,
    )


def _resolve_query(exp_id: Optional[str], wkft: Optional[str]) -> Query:
    if wkft and exp_id:
        query = wkft_to_Query(wkft, exp_id)
    else:
        raise LimsError("Invalid number of arguments supplied.")

    return query


def find_files(
    db_uri: Optional[str] = None,
    exp_id: Optional[str] = None,
    wkft: Optional[str] = None,
) -> list[str]:
    if db_uri is None:
        logger.info("No db_uri supplied, using allen config auto discovery...")
        db_uri = allen_config_auto_discovery("lims_db_uri")
        logger.info("Resolved db_uri: %s" % db_uri)

    query = _resolve_query(exp_id=exp_id, wkft=wkft)
    logger.info("Resolved query: %s" % query)

    with _init_cursor(db_uri) as cursor:
        results = run_query(cursor, query)

    if is_windows():
        logger.info(
            "Windows detected. Fixing paths for windows. Paths before: %s" % results
        )
        fixed = [fix_lims_path(result) for result in results]
        logger.info("Paths after: %s" % fixed)
        return fixed

    return results
