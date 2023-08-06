"""Service commands."""

from fire import Fire
from service import fn
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


Fire(Command)
