from enum import Enum
from pathlib import Path
from typing import Tuple, List

import attr as attr


class MigrationCompatibility(Enum):
    LEGACY = "legacy"
    MODERN = "modern"


@attr.s(kw_only=True, auto_attribs=True)
class MigrationStepContext:
    schema: Tuple[str, List[str]] = None
    # Dir to find migration files from
    # Note: incompatible with 'files'
    dirs: Path = None
    # Files to migrate with
    # Note: incompatible with 'dirs'
    files: List[Path] = None


@attr.s(kw_only=True, auto_attribs=True)
class MigrationContext:
    compatibility: MigrationCompatibility = MigrationCompatibility.LEGACY
    root_pkg_name: object = None
    directory: str = None
    connection_url: str = None
    steps: List[MigrationStepContext] = attr.ib(default=attr.Factory(list))
    migration_context_step_name: str = None
    schema: Tuple[str, List[str]] = None
