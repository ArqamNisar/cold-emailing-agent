"""
logger.py — Centralized logging configuration
==============================================
Sets up a rotating file logger + console handler shared across all modules.

Usage:
    from logger import get_logger
    log = get_logger(__name__)
    log.info("Something happened")
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# ── Config ─────────────────────────────────────────────────────────────────────
LOG_DIR  = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_LEVEL = logging.DEBUG          # change to INFO for production

# Max 5 MB per file, keep 3 backups → 15 MB total on disk
MAX_BYTES  = 5 * 1024 * 1024
BACKUP_COUNT = 3

# ── Formatters ─────────────────────────────────────────────────────────────────
FILE_FMT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
CONSOLE_FMT = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)


def _build_root_logger() -> logging.Logger:
    """Configure and return the root 'cold_email' logger (called once)."""
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger("cold_email")
    root.setLevel(LOG_LEVEL)

    if root.handlers:          # avoid adding duplicate handlers on Streamlit reruns
        return root

    # Rotating file handler
    fh = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(FILE_FMT)
    root.addHandler(fh)

    # Console (visible in the Streamlit terminal)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)      # only INFO+ to console, DEBUG stays in file
    ch.setFormatter(CONSOLE_FMT)
    root.addHandler(ch)

    root.info("Logger initialised — writing to %s", LOG_FILE)
    return root


# Initialise on first import
_build_root_logger()


def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the 'cold_email' hierarchy.

    Parameters
    ----------
    name : str
        Typically __name__ of the calling module.
        e.g. 'cold_email.app', 'cold_email.agents.analyzer_agent'
    """
    # Strip leading package path so the logger name is clean
    short = name.split(".")[-1] if "." in name else name
    return logging.getLogger(f"cold_email.{short}")
