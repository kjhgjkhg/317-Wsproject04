"""
cli_parser.py - 命令行参数定义模块

定义 argparse 子命令（preview / apply / undo）及其参数。
"""

import argparse
from argparse import Namespace

from utils.config import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_PADDING,
    DEFAULT_NUMBER_START,
)


def create_parser() -> argparse.ArgumentParser:
    """
    创建主命令行解析器。

    Returns:
        配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog="rename",
        description="批量文件重命名工具 - 支持多种重命名规则",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  rename preview --prefix "IMG_" --ext jpg,png
  rename apply --suffix "_2025" --yes
  rename undo
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    _add_preview_subparser(subparsers)
    _add_apply_subparser(subparsers)
    _add_undo_subparser(subparsers)

    return parser


def _add_preview_subparser(subparsers: argparse._SubParsersAction) -> None:
    """
    添加 preview 子命令解析器。

    Args:
        subparsers: 子命令解析器组
    """
    preview_parser = subparsers.add_parser(
        "preview",
        help="预览重命名效果（不实际改名）"
    )
    _add_rename_args(preview_parser)


def _add_apply_subparser(subparsers: argparse._SubParsersAction) -> None:
    """
    添加 apply 子命令解析器。

    Args:
        subparsers: 子命令解析器组
    """
    apply_parser = subparsers.add_parser(
        "apply",
        help="执行重命名操作"
    )
    _add_rename_args(apply_parser)
    apply_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="确认执行重命名（不加此参数只预览）"
    )


def _add_undo_subparser(subparsers: argparse._SubParsersAction) -> None:
    """
    添加 undo 子命令解析器。

    Args:
        subparsers: 子命令解析器组
    """
    undo_parser = subparsers.add_parser(
        "undo",
        help="撤销上一次重命名操作"
    )
    undo_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="确认执行撤销"
    )


def _add_rename_args(parser: argparse.ArgumentParser) -> None:
    """
    为解析器添加重命名规则参数。

    Args:
        parser: ArgumentParser 实例
    """
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="添加前缀，如 --prefix 'IMG_'"
    )

    parser.add_argument(
        "--suffix",
        type=str,
        default=None,
        help="添加后缀，如 --suffix '_2025'"
    )

    parser.add_argument(
        "--replace",
        type=str,
        default=None,
        help="字符串替换，格式: old,new，如 --replace 'old,new'"
    )

    parser.add_argument(
        "--number-start",
        type=int,
        default=None,
        help=f"序号起始值，默认 {DEFAULT_NUMBER_START}"
    )

    parser.add_argument(
        "--padding",
        type=int,
        default=None,
        help=f"序号补零位数，默认 {DEFAULT_PADDING}"
    )

    parser.add_argument(
        "--date-format",
        type=str,
        default=None,
        help=f"日期格式插入，如 --date-format '{DEFAULT_DATE_FORMAT.replace('%', '%%')}'"
    )

    parser.add_argument(
        "--regex",
        type=str,
        default=None,
        help="正则替换，格式: pattern,replacement，如 --regex '\\.txt$,\\.bak'"
    )

    parser.add_argument(
        "--ext",
        type=str,
        default=None,
        help="文件扩展名过滤，逗号分隔，如 --ext jpg,png,txt（默认所有文件）"
    )

    parser.add_argument(
        "--sort-by-date",
        action="store_true",
        help="按修改日期排序后再编号"
    )


def parse_args(args: list = None) -> Namespace:
    """
    解析命令行参数。

    Args:
        args: 参数列表，为 None 则从 sys.argv 获取

    Returns:
        解析后的命名空间对象
    """
    parser = create_parser()
    return parser.parse_args(args)


def validate_args(args: Namespace) -> tuple:
    """
    校验参数组合是否合法。

    Args:
        args: 解析后的参数命名空间

    Returns:
        (是否有效, 错误消息列表)
    """
    errors: list = []

    if args.command is None:
        errors.append("请指定子命令: preview, apply 或 undo")

    if hasattr(args, "number_start") and args.number_start is not None:
        if args.number_start < 0:
            errors.append("--number-start 必须为非负整数")

    if hasattr(args, "padding") and args.padding is not None:
        if args.padding < 1:
            errors.append("--padding 必须为正整数")

    return len(errors) == 0, errors
