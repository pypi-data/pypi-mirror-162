"""Service commands."""

import subprocess

from fire import Fire
from service import fn
from pathlib import Path
from uvicorn import run as run_asgi


class Command:
    """Command service."""

    @staticmethod
    def run() -> None:
        """Run service."""
        spec = fn.load_spec()

        entrypoint = spec.pyproject.get('project', {}).get('entrypoint')

        options = {
            'host': spec.socket.host,
            'port': spec.socket.port,
            'use_colors': not fn.running_on_k8s(),
            'log_level': spec.logging.level,
            'access_log': spec.debug,
            'workers': spec.policy.workers,
        }

        if spec.logging.config_file:
            options['log_config'] = spec.logging.config_file

        run_asgi(entrypoint, **options)

    @staticmethod
    def export_locales():
        """Export i18n locales config for locale-gen ."""
        locales = fn.load_locales()
        locales_path = Path(fn.app_dir() / 'locale.gen').resolve()
        with open(locales_path, 'w') as locale_gen:
            for _locale in locales:
                locale_gen.write(f'{_locale}.UTF-8 UTF-8\n')

    @staticmethod
    def migrate():
        """Alembic migrate."""
        subprocess.call(['python', '-m', 'alembic', 'upgrade', 'head'])

    @staticmethod
    def make_migration(name: str):
        """Alembic make migration."""
        subprocess.call(['python', '-m', 'alembic', 'revision', '-m', 'name'])

    @staticmethod
    def rollback(rev: str):
        """Alembic rollback to exact revision."""
        subprocess.call(['python', '-m', 'alembic', 'downgrade', rev])


Fire(Command)
