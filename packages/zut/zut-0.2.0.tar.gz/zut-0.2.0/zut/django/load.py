from __future__ import annotations
import logging, csv
from pathlib import Path
from psycopg2.sql import SQL, Identifier
from django.utils import timezone
from django.db import connections, router, models
from ..format import extended_slugify
from ..outfile import open_outfile
from ..pgsql import call_procedure

logger = logging.getLogger(__name__)

def seed_enum(model_cls: type[models.Model], value_field: str="id", name_field: str="name", attr_fields: list[str]=None):
    if not hasattr(model_cls, "Enum"):
        raise ValueError("model class %s has no Enum attribute" % model_cls)
    enum_class = model_cls.Enum

    for literal in enum_class:
        defaults = {
            name_field: literal.name
        }

        if attr_fields:
            for attr, field in attr_fields.items():
                defaults[field] = getattr(literal, attr)

        kwargs = {
            value_field: literal.value,
            "defaults": defaults
        }
        model_cls.objects.update_or_create(**kwargs)


def load_from_csv(path: Path|str, model_cls: type[models.Model], truncate: bool = True, delimiter = ";", encoding = "utf-8", accept_ignored_headers = True, mapping = None, static_mapping = None) -> int:
    """
    Load from CSV file `path` to model class `model_cls`.
    
    Model class must be defined with a specific manager. Example:

    ```py
    from django.db import models
    from postgres_copy import CopyManager

    class MyModel(models.Model):
        objects = CopyManager()
    ```
    """
    if isinstance(path, str):
        path = Path(path)
        
    if not hasattr(model_cls, "objects") or not hasattr(model_cls.objects, "from_csv"):    
        raise ValueError("missing %s.objects.from_csv, did you specified `objects = CopyManager()`?" % model_cls.__qualname__)

    db_table = model_cls._meta.db_table
    logger.info("load %s in table %s (model %s)", path, db_table, model_cls.__name__)

    fields = [field.name for field in model_cls._meta.get_fields()]

    # Change encoding to utf-8-sig if file starts with UTF8-BOM
    if encoding == "utf-8":
        with open(path, mode="r", encoding="utf-8") as file:
            data = file.read(1)
            if data == "\ufeff":
                encoding = "utf-8-sig"

    # Get CSV headers
    headers = []
    with open(path, newline="", encoding=encoding) as file:
        reader = csv.reader(file, delimiter=delimiter)
        for row in reader:
            headers = row
            break

    if not headers:
        raise ValueError("headers not found in %s", path)

    # Build mapping
    if mapping is None:
        mapping = {}

    def search_field(name, lowersearch):
        """ Returns True to continue headers loop"""
        for field in fields:
            if field.lower() == lowersearch:
                if field in mapping:
                    logger.warning("ignore header \"%s\": cannot map to field \"%s\" (already added mapped to header \"%s\")", name, field, mapping[field])                    
                    return True
                mapping[field] = name
                return True
        return False

    ignored_headers = ""
    for name in headers:
        # Try to find field using lowercase
        if search_field(name, name.lower()):
            continue

        # Try to find field using slug
        slug = extended_slugify(name, separator="_")
        if search_field(name, slug):
            continue

        # Not found in fields
        ignored_headers += (", " if ignored_headers else "") + name + (f" ({slug})" if slug != name else "")

    if ignored_headers:
        logger.log(logging.INFO if accept_ignored_headers else logging.WARNING, "headers ignored in %s: %s", path.name, ignored_headers)

    if static_mapping is None:
        static_mapping = {}
    if "load_at" in fields and not "load_at" in static_mapping:
        static_mapping["load_at"] = timezone.now()
   
    # Truncate table
    if truncate:
        logger.debug("truncate %s (%s)", db_table, model_cls.__name__)

        using = router.db_for_write(model_cls)
        connection = connections[using]
        with connection.cursor() as cursor:
            cursor.execute(SQL("TRUNCATE TABLE {}").format(Identifier(db_table)))

    # Import
    with open(path, newline="", encoding=encoding) as file:
        insert_count = model_cls.objects.from_csv(file, mapping=mapping, static_mapping=static_mapping, delimiter=delimiter)
        logger.info("%d records loaded", insert_count)

    return insert_count


def import_from_query_file(src_connection, sql_path: Path|str, model_cls: type[models.Model] = None, csv_path: Path|str = None, skip: str=False, post_load_procedure: str|list[str] = None,
    truncate: bool = True, delimiter = ";", encoding="utf-8", accept_ignored_headers = True, mapping = None, static_mapping = None) -> int|None:

    """ Export a query in a file to a CSV file and import the CSV file to a model class """
    if not isinstance(sql_path, Path):
        sql_path = Path(sql_path)

    if not csv_path:
        csv_path = sql_path.parent.joinpath("data.local", sql_path.stem + ".csv")
    else:
        if not isinstance(csv_path, Path):
            csv_path = Path(csv_path)
        if csv_path.is_dir():
            csv_path = csv_path.joinpath(sql_path.stem + ".csv")

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    if skip != "extract":
        logger.info(f"extract {sql_path} to {csv_path}")
        with open_outfile(target=csv_path, encoding="utf-8-sig" if encoding == "utf-8" else encoding) as o:
            cursor = src_connection.cursor()
            cursor.execute(sql_path.read_text())

            o.headers = [column[0] for column in cursor.description]

            row = cursor.fetchone()
            while row: 
                o.append_row([value for value in row])
                row = cursor.fetchone()

    if model_cls and skip != "load":
        insert_count = load_from_csv(csv_path, model_cls, truncate=truncate, delimiter=delimiter, encoding=encoding, accept_ignored_headers=accept_ignored_headers, mapping=mapping, static_mapping=static_mapping)

        if post_load_procedure:
            using = router.db_for_write(model_cls)
            dst_connection = connections[using]

            if not isinstance(post_load_procedure, list):
                post_load_procedure = [post_load_procedure]
            for name in post_load_procedure:
                call_procedure(dst_connection, name)
        
        return insert_count
