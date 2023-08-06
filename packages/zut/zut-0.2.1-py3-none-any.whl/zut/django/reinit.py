from __future__ import annotations
import logging, re
from psycopg2.sql import SQL, Literal
from django.conf import settings
from django.db import connection
from django.core.management import base, call_command, get_commands

logger = logging.getLogger(__name__)


def add_arguments(parser):
    parser.add_argument("--drop", dest="action", action="store_const", const="drop")
    parser.add_argument("--bak", dest="action", action="store_const", const="bak")
    parser.add_argument("--bak-to", dest="action", type=str)
    

def handle(action=None, remake_migrations_after={}):
    if not settings.DEBUG:
        raise ValueError("reinit may be used only in DEBUG mode")
    if not action:
        raise ValueError("please confirm what to do with current data: --drop, --bak or --bak-to")

    if action == "drop":
        drop()
    else:
        move_to_schema(action)

    remake_migrations(after=remake_migrations_after)
    
    logger.info("migrate")
    call_command("migrate")

    logger.info("createsuperuser")
    call_command("createsuperuser", "--noinput")

    defined_commands = get_commands()

    if "seed" in defined_commands:
        logger.info("seed")
        call_command("seed")


class Command(base.BaseCommand):
    REMAKE_MIGRATIONS_AFTER = {}

    def add_arguments(self, parser):
        add_arguments(parser)

    def handle(self, action=None, **kwargs):
        handle(action=action, remake_migrations_after=self.REMAKE_MIGRATIONS_AFTER)


def move_to_schema(new_schema, old_schema="public"):
    sql = """do language plpgsql
$$declare
    old_schema name = {};
    new_schema name = {};
    sql_query text;
begin
	sql_query = format('create schema %I', new_schema);

    raise notice 'applying %', sql_query;
    execute sql_query;
   
    for sql_query in
        select
            format('alter %s %I.%I set schema %I', case when table_type = 'VIEW' then 'view' else 'table' end, table_schema, table_name, new_schema)
        from information_schema.tables
        where table_schema = old_schema
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;
end;$$;
"""

    with connection.cursor() as cursor:
        cursor.execute(SQL(sql).format(Literal(old_schema), Literal(new_schema if new_schema else "public")))


def drop(schema="public"):
    sql = """do language plpgsql
$$declare
    old_schema name = {};
    sql_query text;
begin
	-- First, remove foreign-key constraints
    for sql_query in
        select
            format('alter table %I.%I drop constraint %I', table_schema, table_name, constraint_name)
        from information_schema.table_constraints
        where table_schema = old_schema and constraint_type = 'FOREIGN KEY'
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;

	-- Then, drop tables
    for sql_query in
        select
            format('drop %s if exists %I.%I cascade'
                ,case when table_type = 'VIEW' then 'view' else 'table' end
                ,table_schema
                ,table_name
            )
        from information_schema.tables
        where table_schema = old_schema
        and table_name not in ('geography_columns', 'geometry_columns', 'spatial_ref_sys') -- postgis
    loop
        raise notice 'applying %', sql_query;
        execute sql_query;
    end loop;
end;$$;
"""

    with connection.cursor() as cursor:
        cursor.execute(SQL(sql).format(Literal(schema)))


_migration_name_re = re.compile(r"^(\d+)_")

def remake_migrations(after={}):
    # Rename manual migrations to py~
    for path in settings.BASE_DIR.glob("*/migrations/*_manual.py"):
        current = path.as_posix()
        if '.venv/' in current:
            continue
        target = f"{current}~"
        logger.info(f"rename {current} to {target}")
        path.rename(target)
    
    # Delete non-manual migrations
    for path in settings.BASE_DIR.glob("*/migrations/0*.py"):
        current = path.as_posix()
        if current.endswith("_manual.py") or '.venv/' in current:
            continue

        app_name = path.parent.parent.name
        if app_name in after:
            m = _migration_name_re.match(path.name)
            if m:
                migration_number = int(m.group(1))
                if migration_number >= after[app_name]:
                    logger.info(f"delete {current}")
                    path.unlink()
    
    logger.info("make migrations")
    call_command("makemigrations")

    # Rename manual migrations from py~
    for path in settings.BASE_DIR.glob("*/migrations/*_manual.py~"):
        current = path.as_posix()
        if '.venv/' in current:
            continue
        target = current[:-1]
        logger.info(f"rename {current} to {target}")
        path.rename(target)
