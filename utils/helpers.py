"""
utils/helpers.py - 工具函数模块

提供文件遍历、排序、日志读写、表格格式化输出等工具函数。
"""

import os
import json
from typing import List, Dict, Tuple, Optional, Any

from utils.config import (
    SOURCE_DIR,
    OUTPUT_DIR,
    PROTECTED_FILE,
    PREVIEW_FILE,
    LOG_FILE,
    TABLE_BORDER,
    TABLE_SEPARATOR,
)


def get_files_in_directory(
    directory: str,
    extensions: Optional[List[str]] = None,
    include_protected: bool = False
) -> List[str]:
    """
    获取目录中的所有文件（不包括子目录）。

    Args:
        directory: 目标目录路径
        extensions: 文件扩展名过滤列表，为空则不过滤
        include_protected: 是否包含受保护文件

    Returns:
        文件名列表（不含路径）
    """
    if not os.path.isdir(directory):
        return []

    files: List[str] = []
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                if not include_protected and item == PROTECTED_FILE:
                    continue
                if extensions:
                    _, ext = os.path.splitext(item)
                    if ext.lower() not in [e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions]:
                        continue
                files.append(item)
    except PermissionError:
        pass

    return files


def sort_files_by_mtime(directory: str, filenames: List[str]) -> List[Tuple[str, float]]:
    """
    按修改时间排序文件。

    Args:
        directory: 文件所在目录
        filenames: 文件名列表

    Returns:
        排序后的 (文件名, 修改时间) 元组列表
    """
    file_times: List[Tuple[str, float]] = []
    for filename in filenames:
        filepath = os.path.join(directory, filename)
        try:
            mtime = os.path.getmtime(filepath)
            file_times.append((filename, mtime))
        except OSError:
            file_times.append((filename, 0.0))

    file_times.sort(key=lambda x: x[1])
    return file_times


def get_file_mtime(directory: str, filename: str) -> float:
    """
    获取文件的修改时间戳。

    Args:
        directory: 文件所在目录
        filename: 文件名

    Returns:
        修改时间戳
    """
    filepath = os.path.join(directory, filename)
    try:
        return os.path.getmtime(filepath)
    except OSError:
        return 0.0


def format_table(
    headers: List[str],
    rows: List[List[str]],
    column_widths: Optional[List[int]] = None
) -> str:
    """
    格式化输出表格。

    Args:
        headers: 表头列表
        rows: 数据行列表
        column_widths: 列宽列表，为空则自动计算

    Returns:
        格式化后的表格字符串
    """
    if not column_widths:
        column_widths = []
        for i, header in enumerate(headers):
            max_width = len(header)
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            column_widths.append(max_width + 2)

    total_width = sum(column_widths) + len(column_widths) + 1
    border = "=" * total_width
    separator = "-" * total_width

    lines: List[str] = [border]

    header_line = "|"
    for i, header in enumerate(headers):
        header_line += f" {header:<{column_widths[i]}}|"
    lines.append(header_line)
    lines.append(separator)

    for row in rows:
        row_line = "|"
        for i, cell in enumerate(row):
            if i < len(column_widths):
                row_line += f" {str(cell):<{column_widths[i]}}|"
        lines.append(row_line)

    lines.append(border)
    return "\n".join(lines)


def save_preview(
    mappings: List[Tuple[str, str]],
    output_dir: str
) -> str:
    """
    保存预览结果到文件。

    Args:
        mappings: (旧文件名, 新文件名) 元组列表
        output_dir: 输出目录

    Returns:
        保存的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, PREVIEW_FILE)

    headers = ["序号", "原文件名", "新文件名"]
    rows: List[List[str]] = []
    for i, (old_name, new_name) in enumerate(mappings, 1):
        rows.append([str(i), old_name, new_name])

    table = format_table(headers, rows, [6, 35, 35])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("批量文件重命名预览\n")
        f.write(f"共 {len(mappings)} 个文件\n\n")
        f.write(table)

    return output_path


def save_log(
    mappings: List[Tuple[str, str]],
    output_dir: str,
    extra_info: Optional[Dict[str, Any]] = None
) -> str:
    """
    保存操作日志到JSON文件。

    Args:
        mappings: (旧文件名, 新文件名) 元组列表
        output_dir: 输出目录
        extra_info: 额外信息字典

    Returns:
        保存的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, LOG_FILE)

    log_data: Dict[str, Any] = {
        "renamed_files": [{"old": old, "new": new} for old, new in mappings],
        "count": len(mappings),
    }
    if extra_info:
        log_data.update(extra_info)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    return output_path


def load_log(output_dir: str) -> Optional[Dict[str, Any]]:
    """
    从JSON文件加载操作日志。

    Args:
        output_dir: 输出目录

    Returns:
        日志数据字典，文件不存在则返回 None
    """
    log_path = os.path.join(output_dir, LOG_FILE)
    if not os.path.isfile(log_path):
        return None

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def print_preview(mappings: List[Tuple[str, str]]) -> None:
    """
    打印预览表格到控制台。

    Args:
        mappings: (旧文件名, 新文件名) 元组列表
    """
    headers = ["序号", "原文件名", "新文件名"]
    rows: List[List[str]] = []
    for i, (old_name, new_name) in enumerate(mappings, 1):
        rows.append([str(i), old_name, new_name])

    table = format_table(headers, rows, [6, 35, 35])
    print(table)
