"""Input validation utilities for the batch file renaming tool."""
import os
import re
from datetime import datetime
from typing import Tuple, Optional, List

from utils.config import SOURCE_DIR, PROTECTED_FILES, MIN_PADDING, MAX_PADDING


def validate_path(path: str) -> Tuple[bool, str]:
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}"
    if not os.path.isdir(path):
        return False, f"Path is not a directory: {path}"
    return True, "Valid path"


def validate_source_dir() -> Tuple[bool, str]:
    return validate_path(SOURCE_DIR)


def validate_extensions(ext_str: Optional[str]) -> Tuple[bool, str, List[str]]:
    if ext_str is None:
        return True, "No extensions specified (all files allowed)", []
    
    extensions = []
    for ext in ext_str.split(","):
        ext = ext.strip().lower()
        if not ext:
            continue
        if ext.startswith("."):
            ext = ext[1:]
        if not re.match(r"^[a-z0-9_]+$", ext):
            return False, f"Invalid extension: {ext}", []
        extensions.append(ext)
    
    return True, f"Valid extensions: {extensions}", extensions


def validate_replace_pattern(pattern: Optional[str]) -> Tuple[bool, str, Optional[Tuple[str, str]]]:
    if pattern is None:
        return True, "No replace pattern specified", None
    
    parts = pattern.split(",", 1)
    if len(parts) != 2:
        return False, "Replace pattern must be in format 'old,new'", None
    
    old_str, new_str = parts
    if not old_str:
        return False, "Old string cannot be empty in replace pattern", None
    
    return True, f"Valid replace pattern: '{old_str}' -> '{new_str}'", (old_str, new_str)


def validate_regex_pattern(pattern: Optional[str]) -> Tuple[bool, str, Optional[Tuple[str, str]]]:
    if pattern is None:
        return True, "No regex pattern specified", None
    
    parts = pattern.split(",", 1)
    if len(parts) != 2:
        return False, "Regex pattern must be in format 'pattern,replacement'", None
    
    regex_str, replacement = parts
    if not regex_str:
        return False, "Regex pattern cannot be empty", None
    
    try:
        re.compile(regex_str)
    except re.error as e:
        return False, f"Invalid regex pattern: {e}", None
    
    return True, f"Valid regex pattern: '{regex_str}' -> '{replacement}'", (regex_str, replacement)


def validate_date_format(date_format: Optional[str]) -> Tuple[bool, str, Optional[str]]:
    if date_format is None:
        return True, "No date format specified", None
    
    try:
        datetime.now().strftime(date_format)
    except ValueError as e:
        return False, f"Invalid date format: {e}", None
    
    return True, f"Valid date format: {date_format}", date_format


def validate_number_start(number: Optional[int]) -> Tuple[bool, str, Optional[int]]:
    if number is None:
        return True, "No numbering specified", None
    
    if number < 0:
        return False, "Number start must be non-negative", None
    
    return True, f"Valid number start: {number}", number


def validate_padding(padding: Optional[int]) -> Tuple[bool, str, Optional[int]]:
    if padding is None:
        return True, "No padding specified", None
    
    if padding < MIN_PADDING or padding > MAX_PADDING:
        return False, f"Padding must be between {MIN_PADDING} and {MAX_PADDING}", None
    
    return True, f"Valid padding: {padding}", padding


def is_protected_file(filename: str) -> bool:
    basename = os.path.basename(filename)
    return basename in PROTECTED_FILES


def validate_all_args(args) -> Tuple[bool, List[str]]:
    errors = []
    
    is_valid, msg = validate_source_dir()
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_extensions(getattr(args, 'ext', None))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_replace_pattern(getattr(args, 'replace', None))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_regex_pattern(getattr(args, 'regex', None))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_date_format(getattr(args, 'date_format', None))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_number_start(getattr(args, 'number_start', None))
    if not is_valid:
        errors.append(msg)
    
    is_valid, msg, _ = validate_padding(getattr(args, 'padding', None))
    if not is_valid:
        errors.append(msg)
    
    return len(errors) == 0, errors
