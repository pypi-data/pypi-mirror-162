from __future__ import annotations
import logging, re
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import connection, cursor
from pathlib import Path

logger = logging.getLogger(__name__)

_pg_reserved_words = None
_pg_types = None

def get_pg_reserved_words(connection: connection) -> list[str]:
    global _pg_reserved_words
    if _pg_reserved_words is None:
        with connection.cursor() as cursor:
            cursor.execute("select word from pg_get_keywords() where catcode = 'R'")
            _pg_reserved_words = [row[0] for row in cursor.fetchall()]
    return _pg_reserved_words

def get_pg_types(connection: connection) -> dict[int, str]:
    global _pg_types
    if _pg_types is None:
        with connection.cursor() as cursor:
            cursor.execute("select oid, typname from pg_type")
            _pg_types = {row[0]: row[1] for row in cursor.fetchall()}
    return _pg_types

def dictfetchall(cursor: cursor) -> list[dict]:
    """
    Return all rows from a cursor as a dict.
    """ 
    desc = cursor.description 
    return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
    ]

# TODO/FIXME: does not seem to work
# def upgrade_sequence_values(connection: connection, start_with=1001, prefix=None, suffix="_id_seq"):
#     name_like = (prefix if prefix else '') + "%" + (suffix if suffix else '')
#     sequence_names = []
#     with connection.cursor() as cursor:
#         cursor.execute(SQL("select sequencename from pg_sequences where sequencename like {} and start_value = 1 and coalesce(last_value, 0) < {}").format(Literal(name_like), Literal(start_with)))
#         for record in cursor:
#             sequence_names.append(record[0])

#     for sequence_name in sequence_names:
#         with connection.cursor() as cursor:
#             cursor.execute(SQL("alter sequence {} start with {} restart with {}").format(Identifier(sequence_name), Literal(start_with), Literal(start_with)))

ZUT_PGSQL_PATH = Path(__file__).parent

def deploy_paths(connection: connection, *paths):
    actual_paths = []
    for path in paths:
        if isinstance(path, str):
            path = Path(path)
        actual_paths.append(path)

    actual_paths.sort()

    for path in actual_paths:
        if path.is_dir():
            subpaths = sorted(path.iterdir())
            deploy_paths(connection, *subpaths)

        elif not path.name.endswith(".sql"):
            continue # ignore

        elif path.name.endswith("_revert.sql"):
            continue # ignore

        else:
            logger.info("execute %s", path)
            sql = path.read_text()
            with connection.cursor() as cursor:
                cursor.execute(sql)

def revert_paths(connection: connection, *paths):
    actual_paths = []
    for path in paths:
        if isinstance(path, str):
            path = Path(path)
        actual_paths.append(path)

    actual_paths.sort(reverse=True)

    for path in actual_paths:
        if path.is_dir():
            subpaths = sorted(path.iterdir())
            revert_paths(connection, *subpaths)

        elif not path.name.endswith("_revert.sql"):
            continue # ignore

        else:
            logger.info("execute %s", path)
            sql = path.read_text()
            with connection.cursor() as cursor:
                cursor.execute(sql)


def call_procedure(connection: connection, name: str):
    with connection.cursor() as cursor:
        logger.info("call %s", name)
        cursor.execute(SQL("call {}()").format(Identifier(name)))


class PgLogHandler:
    """
    Usage example with Django:

    ```py
    class MainConfig(AppConfig):
        def ready(self):
            connection_created.connect(PgLogHandler.receiver)
    ```
    """

    fullmsg_re = re.compile(r"^(?P<pglevel>[A-Z]+)\:\s(?P<message>.+(?:\r?\n.*)*)$", re.MULTILINE)

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__qualname__)
    
    def append(self, fullmsg: str):
        fullmsg = fullmsg.strip()
        m = self.fullmsg_re.match(fullmsg)
        if not m:
            self.logger.warning(fullmsg)
            return

        message = m.group("message").strip()
        pglevel = m.group("pglevel")
        if pglevel == "EXCEPTION":
            level = logging.ERROR
        elif pglevel == "WARNING":
            level = logging.WARNING
        else:
            level = logging.INFO

        if level <= logging.INFO and message.endswith("\" does not exist, skipping"):
            return

        self.logger.log(level, message)

    @classmethod
    def receiver(cls, sender, connection, **kwargs):
        """ A receiver for django.db.backends.signals.connection_created """
        params = connection.get_connection_params()
        engine = params.get("ENGINE", None)
        if engine and engine != "django.db.backends.postgresql":
            return
            
        connection.connection.notices = cls()
