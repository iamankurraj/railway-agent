import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_base_dir() -> Path:
    return Path(__file__).resolve().parents[1]
