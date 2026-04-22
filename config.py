import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Path Discovery
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# ---------------------------------------------------------------------------
# Environment Variables
# ---------------------------------------------------------------------------
TARGET_DIR = os.getenv("TARGET_DIRECTORY")
DRY_RUN = os.getenv("DRY_RUN", "True").lower() == "true"
API_KEY = os.getenv("GOOGLE_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ---------------------------------------------------------------------------
# Runtime State (set by ai_engine during initialization)
# ---------------------------------------------------------------------------
SELECTED_MODEL = None

# ---------------------------------------------------------------------------
# Official Hierarchy
# ---------------------------------------------------------------------------
REQUIRED_FOLDERS = [
    "01_Personal_Documents",
    "02_Digital_Gallery",
    "03_Studies_and_Career",
    "04_Entertainment",
    "05_Device_Backups"
]

# Added Linux trash folders to ignore list
IGNORE_LIST = [
    "lost+found", ".trash", ".warden-manifest.md",
    ".env", ".git", ".DS_Store", ".Trash-1000", ".Trash-100"
]

# ---------------------------------------------------------------------------
# Structured Logging
# ---------------------------------------------------------------------------
def setup_logging():
    """Configures logging with coloured console output and a rotating file handler.

    Console handler preserves emoji output as-is.
    File handler stores timestamped entries in ``warden_audit.log`` (max 5 MB,
    3 backup rotations).
    """
    logger = logging.getLogger("warden")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Avoid duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # Console handler — keeps emojis readable
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    # Rotating file handler — 5 MB max, 3 backups
    log_file = SCRIPT_DIR / "warden_audit.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)

    return logger
