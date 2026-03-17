"""
utils/config.py - 常量配置模块

定义批量文件重命名工具所需的所有常量、默认路径、支持的日期格式等。
"""

from typing import List, Dict

SOURCE_DIR: str = "./source_data/"
OUTPUT_DIR: str = "./output_build/"
PROTECTED_FILE: str = ".do_not_touch.cfg"

PREVIEW_FILE: str = "rename_preview.txt"
LOG_FILE: str = "rename_log.json"

DEFAULT_EXTENSIONS: List[str] = []
SUPPORTED_DATE_FORMATS: List[str] = [
    "%Y%m%d",
    "%Y-%m-%d",
    "%Y%m%d_%H%M%S",
    "%Y-%m-%d_%H-%M-%S",
    "%d%m%Y",
    "%d-%m-%Y",
]

DEFAULT_DATE_FORMAT: str = "%Y%m%d"
DEFAULT_PADDING: int = 3
DEFAULT_NUMBER_START: int = 1

TABLE_BORDER: str = "=" * 80
TABLE_SEPARATOR: str = "-" * 80

ERROR_MESSAGES: Dict[str, str] = {
    "source_not_found": "错误：源目录不存在: {path}",
    "output_not_found": "错误：输出目录不存在: {path}",
    "protected_file": "错误：禁止操作受保护文件: {filename}",
    "file_exists": "错误：目标文件已存在: {filename}",
    "invalid_regex": "错误：无效的正则表达式: {pattern}",
    "invalid_date_format": "错误：无效的日期格式: {fmt}",
    "invalid_extension": "错误：无效的扩展名格式: {ext}",
    "no_files_found": "警告：未找到符合条件的文件",
    "permission_denied": "错误：权限不足，无法操作文件: {filename}",
    "log_not_found": "错误：日志文件不存在，无法撤销",
    "undo_success": "成功撤销 {count} 个文件的重命名操作",
    "preview_saved": "预览结果已保存到: {path}",
    "log_saved": "操作日志已保存到: {path}",
}
