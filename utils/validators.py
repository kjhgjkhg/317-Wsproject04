"""
utils/validators.py - 输入校验模块

提供扩展名、日期格式、正则合法性、路径存在等校验功能。
"""

import os
import re
from datetime import datetime
from typing import List, Tuple, Optional

from utils.config import (
    SOURCE_DIR,
    OUTPUT_DIR,
    PROTECTED_FILE,
    SUPPORTED_DATE_FORMATS,
    ERROR_MESSAGES,
)


def validate_directory(path: str, must_exist: bool = True) -> Tuple[bool, str]:
    """
    校验目录是否存在且可访问。

    Args:
        path: 目录路径
        must_exist: 是否必须存在

    Returns:
        (是否有效, 错误消息)
    """
    if must_exist and not os.path.isdir(path):
        return False, ERROR_MESSAGES["source_not_found"].format(path=path)

    if os.path.isdir(path):
        if not os.access(path, os.R_OK):
            return False, ERROR_MESSAGES["permission_denied"].format(filename=path)

    return True, ""


def validate_source_directory() -> Tuple[bool, str]:
    """
    校验源目录是否存在。

    Returns:
        (是否有效, 错误消息)
    """
    return validate_directory(SOURCE_DIR, must_exist=True)


def validate_output_directory() -> Tuple[bool, str]:
    """
    校验输出目录是否存在，不存在则创建。

    Returns:
        (是否有效, 错误消息)
    """
    if not os.path.isdir(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        except PermissionError:
            return False, ERROR_MESSAGES["permission_denied"].format(filename=OUTPUT_DIR)

    return True, ""


def validate_extensions(extensions: List[str]) -> Tuple[bool, str]:
    """
    校验扩展名格式。

    Args:
        extensions: 扩展名列表

    Returns:
        (是否有效, 错误消息)
    """
    for ext in extensions:
        if not ext or not isinstance(ext, str):
            return False, ERROR_MESSAGES["invalid_extension"].format(ext=ext)

        clean_ext = ext.lstrip(".")
        if not clean_ext or not re.match(r"^[a-zA-Z0-9]+$", clean_ext):
            return False, ERROR_MESSAGES["invalid_extension"].format(ext=ext)

    return True, ""


def validate_date_format(fmt: str) -> Tuple[bool, str]:
    """
    校验日期格式是否合法。

    Args:
        fmt: 日期格式字符串

    Returns:
        (是否有效, 错误消息)
    """
    try:
        datetime.now().strftime(fmt)
        return True, ""
    except (ValueError, TypeError):
        return False, ERROR_MESSAGES["invalid_date_format"].format(fmt=fmt)


def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
    """
    校验正则表达式是否合法。

    Args:
        pattern: 正则表达式模式

    Returns:
        (是否有效, 错误消息)
    """
    try:
        re.compile(pattern)
        return True, ""
    except re.error:
        return False, ERROR_MESSAGES["invalid_regex"].format(pattern=pattern)


def validate_regex_replace(regex_str: str) -> Tuple[bool, str, str, str]:
    """
    校验正则替换字符串格式。

    Args:
        regex_str: 格式为 "pattern,replacement" 的字符串

    Returns:
        (是否有效, 错误消息, pattern, replacement)
    """
    if not regex_str:
        return False, "正则替换参数不能为空", "", ""

    parts = regex_str.split(",", 1)
    if len(parts) != 2:
        return False, "正则替换格式应为: pattern,replacement", "", ""

    pattern, replacement = parts[0], parts[1]
    is_valid, error = validate_regex_pattern(pattern)
    if not is_valid:
        return False, error, "", ""

    return True, "", pattern, replacement


def validate_replace_string(replace_str: str) -> Tuple[bool, str, str, str]:
    """
    校验字符串替换格式。

    Args:
        replace_str: 格式为 "old,new" 的字符串

    Returns:
        (是否有效, 错误消息, old_str, new_str)
    """
    if not replace_str:
        return False, "替换参数不能为空", "", ""

    parts = replace_str.split(",", 1)
    if len(parts) != 2:
        return False, "替换格式应为: old,new", "", ""

    return True, "", parts[0], parts[1]


def is_protected_file(filename: str) -> bool:
    """
    检查文件是否为受保护文件。

    Args:
        filename: 文件名

    Returns:
        是否为受保护文件
    """
    return filename == PROTECTED_FILE


def check_filename_conflict(
    directory: str,
    old_name: str,
    new_name: str
) -> Tuple[bool, str]:
    """
    检查重命名是否会产生文件名冲突。

    Args:
        directory: 文件所在目录
        old_name: 原文件名
        new_name: 新文件名

    Returns:
        (是否有冲突, 冲突消息)
    """
    if old_name == new_name:
        return False, ""

    new_path = os.path.join(directory, new_name)
    if os.path.exists(new_path):
        return True, ERROR_MESSAGES["file_exists"].format(filename=new_name)

    return False, ""


def check_multiple_conflicts(
    directory: str,
    mappings: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    """
    批量检查文件名冲突。

    Args:
        directory: 文件所在目录
        mappings: (旧文件名, 新文件名) 元组列表

    Returns:
        冲突列表 [(旧文件名, 冲突消息)]
    """
    conflicts: List[Tuple[str, str]] = []
    new_names_seen: dict = {}

    for old_name, new_name in mappings:
        has_conflict, msg = check_filename_conflict(directory, old_name, new_name)
        if has_conflict:
            conflicts.append((old_name, msg))

        if new_name in new_names_seen:
            conflicts.append((old_name, f"新文件名重复: {new_name}"))
        else:
            new_names_seen[new_name] = old_name

    return conflicts
