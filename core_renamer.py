"""
core_renamer.py - 重命名规则解析与文件名生成核心模块

负责解析重命名规则并生成新文件名。
"""

import os
import re
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from utils.config import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_PADDING,
    DEFAULT_NUMBER_START,
)
from utils.helpers import get_file_mtime
from utils.validators import (
    validate_regex_pattern,
    validate_date_format,
)


class RenameRule:
    """重命名规则配置类。"""

    def __init__(
        self,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        replace_old: Optional[str] = None,
        replace_new: Optional[str] = None,
        number_start: int = DEFAULT_NUMBER_START,
        padding: int = DEFAULT_PADDING,
        date_format: Optional[str] = None,
        regex_pattern: Optional[str] = None,
        regex_replacement: Optional[str] = None,
        sort_by_date: bool = False
    ):
        """
        初始化重命名规则。

        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀
            replace_old: 要替换的旧字符串
            replace_new: 替换后的新字符串
            number_start: 序号起始值
            padding: 序号补零位数
            date_format: 日期格式
            regex_pattern: 正则模式
            regex_replacement: 正则替换字符串
            sort_by_date: 是否按日期排序
        """
        self.prefix = prefix
        self.suffix = suffix
        self.replace_old = replace_old
        self.replace_new = replace_new
        self.number_start = number_start
        self.padding = padding
        self.date_format = date_format
        self.regex_pattern = regex_pattern
        self.regex_replacement = regex_replacement
        self.sort_by_date = sort_by_date

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "prefix": self.prefix,
            "suffix": self.suffix,
            "replace_old": self.replace_old,
            "replace_new": self.replace_new,
            "number_start": self.number_start,
            "padding": self.padding,
            "date_format": self.date_format,
            "regex_pattern": self.regex_pattern,
            "regex_replacement": self.regex_replacement,
            "sort_by_date": self.sort_by_date,
        }


class CoreRenamer:
    """核心重命名器类。"""

    def __init__(self, rule: RenameRule):
        """
        初始化重命名器。

        Args:
            rule: 重命名规则对象
        """
        self.rule = rule
        self._validate_rule()

    def _validate_rule(self) -> None:
        """校验规则参数合法性。"""
        if self.rule.regex_pattern:
            is_valid, _ = validate_regex_pattern(self.rule.regex_pattern)
            if not is_valid:
                raise ValueError(f"无效的正则表达式: {self.rule.regex_pattern}")

        if self.rule.date_format:
            is_valid, _ = validate_date_format(self.rule.date_format)
            if not is_valid:
                raise ValueError(f"无效的日期格式: {self.rule.date_format}")

    def generate_new_name(
        self,
        old_name: str,
        index: int,
        directory: str
    ) -> str:
        """
        根据规则生成新文件名。

        Args:
            old_name: 原文件名
            index: 文件序号
            directory: 文件所在目录

        Returns:
            新文件名
        """
        name, ext = os.path.splitext(old_name)
        new_name = name
        new_ext = ext

        if self.rule.replace_old and self.rule.replace_new is not None:
            new_name = new_name.replace(self.rule.replace_old, self.rule.replace_new)

        if self.rule.regex_pattern and self.rule.regex_replacement is not None:
            try:
                new_name = re.sub(
                    self.rule.regex_pattern,
                    self.rule.regex_replacement,
                    new_name
                )
            except re.error:
                pass

        if self.rule.date_format:
            mtime = get_file_mtime(directory, old_name)
            date_str = datetime.fromtimestamp(mtime).strftime(self.rule.date_format)
            new_name = f"{new_name}_{date_str}"

        if self.rule.number_start is not None:
            num = self.rule.number_start + index
            num_str = str(num).zfill(self.rule.padding)
            new_name = f"{new_name}_{num_str}"

        if self.rule.prefix:
            new_name = f"{self.rule.prefix}{new_name}"

        if self.rule.suffix:
            new_name = f"{new_name}{self.rule.suffix}"

        return f"{new_name}{new_ext}"

    def generate_all_names(
        self,
        filenames: List[str],
        directory: str,
        sorted_by_mtime: List[Tuple[str, float]] = None
    ) -> List[Tuple[str, str]]:
        """
        批量生成新文件名。

        Args:
            filenames: 原文件名列表
            directory: 文件所在目录
            sorted_by_mtime: 按修改时间排序的文件列表

        Returns:
            (旧文件名, 新文件名) 元组列表
        """
        mappings: List[Tuple[str, str]] = []

        if self.rule.sort_by_date and sorted_by_mtime:
            for index, (filename, _) in enumerate(sorted_by_mtime):
                new_name = self.generate_new_name(filename, index, directory)
                mappings.append((filename, new_name))
        else:
            for index, filename in enumerate(filenames):
                new_name = self.generate_new_name(filename, index, directory)
                mappings.append((filename, new_name))

        return mappings


def create_rule_from_args(args) -> RenameRule:
    """
    从命令行参数创建重命名规则。

    Args:
        args: argparse 解析后的参数对象

    Returns:
        RenameRule 实例
    """
    replace_old = None
    replace_new = None
    if hasattr(args, "replace") and args.replace:
        parts = args.replace.split(",", 1)
        if len(parts) == 2:
            replace_old, replace_new = parts[0], parts[1]

    regex_pattern = None
    regex_replacement = None
    if hasattr(args, "regex") and args.regex:
        parts = args.regex.split(",", 1)
        if len(parts) == 2:
            regex_pattern, regex_replacement = parts[0], parts[1]

    return RenameRule(
        prefix=getattr(args, "prefix", None),
        suffix=getattr(args, "suffix", None),
        replace_old=replace_old,
        replace_new=replace_new,
        number_start=getattr(args, "number_start", DEFAULT_NUMBER_START),
        padding=getattr(args, "padding", DEFAULT_PADDING),
        date_format=getattr(args, "date_format", None),
        regex_pattern=regex_pattern,
        regex_replacement=regex_replacement,
        sort_by_date=getattr(args, "sort_by_date", False),
    )
