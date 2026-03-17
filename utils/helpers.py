"""Helper functions for file operations, logging, and output formatting."""
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional

from utils.config import SOURCE_DIR, OUTPUT_DIR, LOG_FILE, PREVIEW_FILE
from utils.validators import is_protected_file


def ensure_output_dir() -> bool:
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        return True
    except (OSError, IOError) as e:
        print(f"Error creating output directory: {e}")
        return False


def get_files_from_source(extensions: Optional[List[str]] = None) -> List[str]:
    files = []
    try:
        for entry in os.listdir(SOURCE_DIR):
            full_path = os.path.join(SOURCE_DIR, entry)
            if os.path.isfile(full_path):
                if is_protected_file(entry):
                    continue
                if extensions:
                    file_ext = os.path.splitext(entry)[1].lower().lstrip(".")
                    if file_ext not in extensions:
                        continue
                files.append(entry)
    except (OSError, IOError) as e:
        print(f"Error reading source directory: {e}")
        return []
    
    files.sort()
    return files


def get_file_mtime(filename: str) -> Optional[datetime]:
    filepath = os.path.join(SOURCE_DIR, filename)
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime)
    except (OSError, IOError):
        return None


def format_as_table(mappings: List[Tuple[str, str]]) -> str:
    if not mappings:
        return "No files to process.\n"
    
    max_old_len = max(len(old) for old, _ in mappings)
    max_new_len = max(len(new) for _, new in mappings)
    
    max_old_len = max(max_old_len, len("Old Filename"))
    max_new_len = max(max_new_len, len("New Filename"))
    
    lines = []
    header = f"| {'Old Filename':<{max_old_len}} | {'New Filename':<{max_new_len}} |"
    separator = f"+{'-' * (max_old_len + 2)}+{'-' * (max_new_len + 2)}+"
    
    lines.append(separator)
    lines.append(header)
    lines.append(separator)
    
    for old_name, new_name in mappings:
        lines.append(f"| {old_name:<{max_old_len}} | {new_name:<{max_new_len}} |")
    
    lines.append(separator)
    return "\n".join(lines) + "\n"


def save_preview(mappings: List[Tuple[str, str]]) -> bool:
    if not ensure_output_dir():
        return False
    
    table_content = format_as_table(mappings)
    
    try:
        with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
            f.write("=== Rename Preview ===\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(table_content)
        return True
    except (OSError, IOError) as e:
        print(f"Error saving preview: {e}")
        return False


def save_log(mappings: Dict[str, str]) -> bool:
    if not ensure_output_dir():
        return False
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "operations": mappings
    }
    
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)
        return True
    except (OSError, IOError) as e:
        print(f"Error saving log: {e}")
        return False


def load_log() -> Optional[Dict[str, str]]:
    try:
        if not os.path.exists(LOG_FILE):
            print(f"Log file not found: {LOG_FILE}")
            return None
        
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        operations = data.get("operations", {})
        if not isinstance(operations, dict):
            print("Invalid log format")
            return None
        
        return operations
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"Error loading log: {e}")
        return None


def split_name_ext(filename: str) -> Tuple[str, str]:
    basename = os.path.basename(filename)
    name, ext = os.path.splitext(basename)
    return name, ext


def join_name_ext(name: str, ext: str) -> str:
    if ext.startswith("."):
        return f"{name}{ext}"
    return f"{name}.{ext}" if ext else name
