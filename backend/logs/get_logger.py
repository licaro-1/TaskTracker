import loguru

from core.settings import BASE_DIR


def set_logger(file_path: str, level: str, rotation: str, compression: str):
    log = loguru.logger
    log.add(file_path, level=level, rotation=rotation, compression=compression)
    return log


logger = set_logger(
    f"{BASE_DIR / 'logs/' / 'log_backup/' / 'tracker.log'}",
    level="WARNING",
    rotation="250 MB",
    compression="zip",
)
