import contextlib
import logging
import shutil
import urllib
import uuid
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Iterator, Optional, List
from unittest.mock import patch
from urllib import parse

from yoyo import get_backend
from yoyo import read_migrations
from yoyo.backends import PostgresqlBackend
from yoyo.connections import BACKENDS

from constellate.database.common.databasetype import DatabaseType
from constellate.database.migration.migration_step import (
    get_module_from_path,
    migration_steps_modern,
)
from constellate.database.migration.migrationaction import MigrationAction
from constellate.database.migration.migrationcontext import (
    MigrationContext,
    MigrationStepContext,
    MigrationCompatibility,
)
from constellate.storage.filesystem.tmpfs.rambacked import mkd_tmpfs


@contextmanager
def _patch_yoyo_postgres_backend_impl() -> Iterator[None]:
    class _PostgresqlBackend2(PostgresqlBackend):
        def cursor(self):
            cursor = super().cursor()
            if self.schema:
                # Make sure connection has search path set with schema
                cursor.execute("SET search_path TO {}".format(self.schema))
            return cursor

    # Replace PostgresBackend with customized PostgresBackend
    BACKENDS2 = dict(BACKENDS)
    for k, v in BACKENDS.items():
        if v is PostgresqlBackend:
            BACKENDS2.update({k: _PostgresqlBackend2})

    with patch("yoyo.connections.BACKENDS", BACKENDS2) as patched:
        yield None


@contextmanager
def _patch_yoyo_no_backend_impl() -> Iterator[None]:
    yield None


def _migrate_with_yoyo(
    migration_context: MigrationContext = None,
    action: MigrationAction = MigrationAction.UNKNOWN,
    logger: logging.Logger = None,
    db_type: DatabaseType = None,
) -> None:
    """Run database migrations using yoyo library: https://ollycope.com/software/yoyo/latest/#migrations-as-sql-scripts"""

    class Handler(logging.Handler):
        def __init__(self, level: int = logging.NOTSET, target_logger: logging.Logger = None):
            super(Handler, self).__init__(level=level)
            self._target_logger = target_logger

        def emit(self, record: logging.LogRecord) -> None:
            if self._target_logger is not None:
                self._target_logger.log(level=record.levelno, msg=record.getMessage())

        def flush(self) -> None:
            if self._target_logger is not None:
                for _handler in self._target_logger.handlers:
                    _handler.flush()

    handler = Handler(level=logging.DEBUG, target_logger=logger)
    # Append temporary Handler to yoyo's library
    yoyo_logger = getLogger("yoyo.migrations")
    yoyo_logger.setLevel(logging.DEBUG)

    # Patch yoyo backends when necessary
    _patch_yoyo_backend = None
    if db_type == DatabaseType.POSTGRESQL:
        _patch_yoyo_backend = _patch_yoyo_postgres_backend_impl
    else:
        _patch_yoyo_backend = _patch_yoyo_no_backend_impl

    def edit_connection_url_schema(url: str = None, schema: str = None):
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))

        if schema is not None:
            query.update({"schema": schema})

        url_parts[4] = urllib.parse.urlencode(query)

        return urllib.parse.urlunparse(url_parts)

    for migration_context_step in migration_context.steps:
        schema = (
            migration_context_step.schema
            if migration_context_step.schema is not None
            else migration_context.schema
        )
        connection_url = (
            edit_connection_url_schema(url=migration_context.connection_url, schema=schema)
            if db_type == DatabaseType.POSTGRESQL
            else migration_context.connection_url
        )
        migration_dirs = migration_context_step.dirs
        migration_files = migration_context_step.files
        try:
            yoyo_logger.addHandler(handler)

            with _patch_yoyo_backend() as _:
                backend = None
                try:

                    def _migrating(backend, migrations):
                        # Run migration
                        with backend.lock():
                            if action == MigrationAction.UP:
                                # Apply any outstanding migrations
                                backend.apply_migrations(backend.to_apply(migrations))
                            elif action == MigrationAction.DOWN:
                                # Rollback all migrations
                                backend.rollback_migrations(backend.to_rollback(migrations))

                    @contextmanager
                    def root_dir_wrapper(
                        item: Path = None,
                        last_path: bool = False,
                        post_apply_last: bool = True,
                        post_apply_names: List[str] = None,
                    ):
                        is_file = item.exists() and item.is_file()
                        location = (
                            mkd_tmpfs(prefix="constellate.migrate", suffix=str(uuid.uuid4()))
                            if is_file
                            else contextlib.nullcontext(enter_result=item)
                        )
                        with location as dir_path:
                            if is_file:

                                if item.name in post_apply_names:
                                    # Do not execute post_apply files on their own
                                    dir_path = None
                                else:
                                    # Copy migration file
                                    # src: https://stackoverflow.com/a/30359308/219728
                                    shutil.copy2(item, dir_path)

                                    # Copy eventual post_apply migration file
                                    if last_path and post_apply_last:
                                        post_apply_paths = [
                                            item.with_name(name) for name in post_apply_names
                                        ]
                                        for post_apply_path in post_apply_paths:
                                            if post_apply_path.exists():
                                                shutil.copy2(post_apply_path, dir_path)

                            yield dir_path

                            if is_file:
                                # Note: Upon exiting the context (for file only!), the temporary dir
                                # is deleted
                                pass

                    # Prepare migration
                    backend = get_backend(connection_url)

                    # Migrate each item individually to ensure consistent migration order
                    post_apply_names = ["post-apply.sql", "post-apply.py"]
                    paths = migration_files or migration_dirs
                    paths = list(filter(lambda p: p.name not in post_apply_names, paths))
                    count = len(paths)
                    for index, path in enumerate(paths, start=1):
                        # 'read_migrations' only accepts directories.
                        # Workaround: Creating 1 director per file to migrate
                        with root_dir_wrapper(
                            item=path,
                            last_path=index == count,
                            post_apply_last=True,
                            post_apply_names=post_apply_names,
                        ) as p:
                            if p is not None:
                                migrations = read_migrations(*[str(p)])
                                _migrating(backend, migrations)
                except BaseException as e:
                    raise
                finally:
                    # Remove lock, regardless of migration status
                    if backend is not None:
                        backend.break_lock()
        finally:
            yoyo_logger.removeHandler(handler)


def _migrate_unsupported(
    migration_context: MigrationContext = None,
    action: MigrationAction = MigrationAction.UNKNOWN,
    logger: logging.Logger = None,
    db_type: DatabaseType = None,
):
    raise NotImplementedError()


def migrate(
    database_type: DatabaseType = DatabaseType.UNKNOWN,
    connection_url: str = None,
    migration_dirs: List[Path] = None,
    migration_context: MigrationContext = None,
    action: MigrationAction = MigrationAction.UNKNOWN,
    logger: logging.Logger = None,
) -> None:
    """Run database migrations.
    :migration_dirs: List of directory contains SQL file scripts (or equivalent)
                     SQL file scripts must be named with script alphabetic order:
                     - 0001.up.foobar.sql
                     - 0001.down.foobar.sql
                     - 0002.up.zoobar.sql
                     - etc ...
    :raises:
        BaseException When migration fails
    """
    run_migration = {
        DatabaseType.SQLITE: _migrate_with_yoyo,
        DatabaseType.POSTGRESQL: _migrate_with_yoyo,
    }.get(database_type, _migrate_unsupported)

    migration_contexts = []
    if len(migration_dirs) > 0:
        # Legacy context
        def to_migration_context(
            migration_dir: Path = None, connection_url: str = None
        ) -> MigrationContext:
            a_module = get_module_from_path(path=Path.joinpath(migration_dir, "__init__.py"))
            migration_context = MigrationContext(
                connection_url=connection_url, compatibility=MigrationCompatibility.LEGACY
            )
            migration_context.steps.append(MigrationStepContext(schema=None, dirs=[migration_dir]))
            return migration_context

        migration_contexts.extend(
            [
                to_migration_context(migration_dir=migration_dir, connection_url=connection_url)
                for migration_dir in migration_dirs
            ]
        )
    else:
        # Modern context: Auto populate steps
        if len(migration_context.steps) == 0:
            # Auto populate connection url
            migration_context.connection_url = connection_url
            # Auto populate migration steps
            kwargs = {}
            if migration_context.migration_context_step_name:
                kwargs.update(
                    {"migration_context_step_name": migration_context.migration_context_step_name}
                )
            migration_steps_modern(migration_context=migration_context, **kwargs)
        migration_contexts.append(migration_context)

    for migration_ctx in migration_contexts:
        run_migration(
            migration_context=migration_ctx,
            action=action,
            logger=logger,
            db_type=database_type,
        )
