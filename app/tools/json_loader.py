import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any
from app.utils import get_base_dir

logger = logging.getLogger(__name__)

@lru_cache(maxsize=32)
def load_json(rel_path: str) -> Any:
    """
    Loads a JSON file from the /data directory relative to project base.
    Uses caching for efficiency.
    """
    base_dir = get_base_dir()
    data_dir = base_dir / "data"
    file_path = (data_dir / rel_path).resolve()

    if not file_path.exists():
        logger.error("JSON file not found: %s", file_path)
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", file_path, e)
        raise
