import logging
import sys


class _CtxFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "ctx"):
            record.ctx = "-"
        return True


def init_logging(level="INFO", json_format=False):
    """Initialize stdout/stderr split logging with a stable context field."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))

    # Avoid duplicate handlers if called multiple times.
    if root.handlers:
        return

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(_CtxFilter())

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.addFilter(_CtxFilter())

    if json_format:
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"msg":"%(message)s","ctx":"%(ctx)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s [ctx:%(ctx)s]"
        )

    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    root.addHandler(stdout_handler)
    root.addHandler(stderr_handler)
