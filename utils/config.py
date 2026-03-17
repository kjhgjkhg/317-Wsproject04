"""Configuration constants for the batch file renaming tool."""
import os
from typing import List, Dict, Any

SOURCE_DIR: str = os.path.join(".", "source_data")
OUTPUT_DIR: str = os.path.join(".", "output_build")

PREVIEW_FILE: str = os.path.join(OUTPUT_DIR, "rename_preview.txt")
LOG_FILE: str = os.path.join(OUTPUT_DIR, "rename_log.json")

PROTECTED_FILES: List[str] = [".do_not_touch.cfg"]

DEFAULT_DATE_FORMAT: str = "%Y%m%d"
SUPPORTED_DATE_FORMATS: List[str] = [
    "%Y%m%d",
    "%Y-%m-%d",
    "%d%m%Y",
    "%d-%m-%Y",
    "%Y%m%d_%H%M%S",
    "%Y-%m-%d_%H-%M-%S",
]

DEFAULT_PADDING: int = 3
MIN_PADDING: int = 1
MAX_PADDING: int = 10

EXIT_SUCCESS: int = 0
EXIT_ERROR: int = 1
