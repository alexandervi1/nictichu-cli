import sys
from pathlib import Path
from loguru import logger


def setup_logger():
    settings_module = __import__('src.utils.config', fromlist=['get_settings'])
    settings = settings_module.get_settings()
    
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    log_dir = Path.home() / ".nictichu" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "nictichu_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level="DEBUG",
        encoding="utf-8"
    )


def get_logger():
    return logger
