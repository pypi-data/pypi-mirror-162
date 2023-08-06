import importlib
from pathlib import Path
from types import ModuleType
from typing import Optional, List

from deprecated.classic import deprecated
from yoyo import step

from constellate.database.migration.migrationcontext import MigrationContext, MigrationStepContext
from constellate.resource.resource import get_folder


@deprecated(
    version="0.6.13",
    reason="Use migration_step2 instead",
)
def migration_steps_legacy(migration_dir: Path = None, suffix: str = "*.sql.txt") -> List[object]:
    def read_content(file: Path = None):
        with open(file) as f:
            return f.read()

    def alphabetically_sorted_files(migration_dir: Path = None):
        files = [str(f) for f in list(Path(migration_dir).glob(suffix))]
        return sorted(files)

    return [
        step(read_content(file=file))
        for file in alphabetically_sorted_files(migration_dir=migration_dir)
    ]


def migration_files_collect(migration_dir: Path = None, suffix: str = "*.sql") -> List[Path]:
    def alphabetically_sorted_files(migration_dir: Path = None):
        files = [str(f) for f in list(Path(migration_dir).glob(suffix))]
        return [Path(f) for f in sorted(files)]

    return [file for file in alphabetically_sorted_files(migration_dir=migration_dir)]


def migration_steps_modern(
    migration_context: MigrationContext = None,
    migration_context_step_name: str = "migration_context_step.py",
) -> None:
    migration_dir = get_folder(
        root_pkg_name=migration_context.root_pkg_name.__package__,
        directory=migration_context.directory,
    )
    step_dirs = [f for f in migration_dir.iterdir() if f.is_dir()]
    step_dirs = sorted(step_dirs, key=lambda x: str(x))

    steps = []
    for step_dir in step_dirs:
        step_files = [f for f in step_dir.glob(f"*{migration_context_step_name}")]
        step_files = sorted(step_files, key=lambda x: str(x))
        has_custom_migration_context = len(step_files) == 1

        if has_custom_migration_context:
            for step_file in step_files:
                step_module = get_module_from_path(path=step_file)

                schema = getattr(step_module, "schema", None)
                if not isinstance(schema, (type(None), str, type(List[str]))):
                    raise ValueError()

                dir = getattr(step_module, "migration_dir", None)
                if not isinstance(dir, (type(None), Path)):
                    raise ValueError()

                files = getattr(step_module, "migration_files", None)
                if not isinstance(files, (type(None), List[str])):
                    raise ValueError()

                has_files = files is not None
                if dir is not None and not has_files:
                    files = migration_files_collect(migration_dir=dir)

                kwargs = {}
                if schema is not None:
                    kwargs.update({"schema": schema})
                if files is not None:
                    kwargs.update({"files": files})
                elif dir is not None:
                    kwargs.update({"dirs": [dir]})
                else:
                    # Either a migration dir is specified or individual files
                    raise NotImplementedError()

                steps.append(MigrationStepContext(**kwargs))
        else:
            pass

    migration_context.steps = steps


def get_module_from_path(path: Path = None) -> ModuleType:
    module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    step_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(step_module)
    return step_module
