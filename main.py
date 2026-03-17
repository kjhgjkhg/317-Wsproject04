"""
main.py - 程序入口模块

argparse 子命令解析与流程控制。
"""

import sys
from typing import List, Optional

from cli_parser import parse_args, validate_args
from core_renamer import CoreRenamer, create_rule_from_args
from rename_engine import RenameEngine
from utils.config import (
    SOURCE_DIR,
    OUTPUT_DIR,
    DEFAULT_PADDING,
    DEFAULT_NUMBER_START,
)
from utils.validators import validate_extensions


def main(args: Optional[List[str]] = None) -> int:
    """
    主函数入口。

    Args:
        args: 命令行参数列表，为 None 则从 sys.argv 获取

    Returns:
        退出码（0 表示成功，非 0 表示失败）
    """
    parsed_args = parse_args(args)

    is_valid, errors = validate_args(parsed_args)
    if not is_valid:
        for error in errors:
            print(f"错误: {error}")
        return 1

    engine = RenameEngine(SOURCE_DIR, OUTPUT_DIR)

    is_valid, errors = engine.validate_directories()
    if not is_valid:
        for error in errors:
            print(error)
        return 1

    if parsed_args.command == "preview":
        return _handle_preview(parsed_args, engine)
    elif parsed_args.command == "apply":
        return _handle_apply(parsed_args, engine)
    elif parsed_args.command == "undo":
        return _handle_undo(parsed_args, engine)
    else:
        print("未知命令，请使用 -h 查看帮助")
        return 1


def _handle_preview(args, engine: RenameEngine) -> int:
    """
    处理 preview 子命令。

    Args:
        args: 解析后的参数
        engine: 重命名引擎实例

    Returns:
        退出码
    """
    extensions = _parse_extensions(args.ext)

    if extensions:
        is_valid, error = validate_extensions(extensions)
        if not is_valid:
            print(error)
            return 1

    files = engine.get_target_files(extensions)

    if not files:
        print("未找到符合条件的文件")
        return 0

    rule = create_rule_from_args(args)

    try:
        renamer = CoreRenamer(rule)
    except ValueError as e:
        print(f"错误: {e}")
        return 1

    sorted_files = None
    if rule.sort_by_date:
        sorted_files = engine.get_sorted_files(files)

    mappings = renamer.generate_all_names(files, SOURCE_DIR, sorted_files)

    success, message = engine.preview(mappings, save_to_file=True)

    if success:
        print(f"\n{message}")
        return 0
    else:
        print(f"\n错误: {message}")
        return 1


def _handle_apply(args, engine: RenameEngine) -> int:
    """
    处理 apply 子命令。

    Args:
        args: 解析后的参数
        engine: 重命名引擎实例

    Returns:
        退出码
    """
    extensions = _parse_extensions(args.ext)

    if extensions:
        is_valid, error = validate_extensions(extensions)
        if not is_valid:
            print(error)
            return 1

    files = engine.get_target_files(extensions)

    if not files:
        print("未找到符合条件的文件")
        return 0

    rule = create_rule_from_args(args)

    try:
        renamer = CoreRenamer(rule)
    except ValueError as e:
        print(f"错误: {e}")
        return 1

    sorted_files = None
    if rule.sort_by_date:
        sorted_files = engine.get_sorted_files(files)

    mappings = renamer.generate_all_names(files, SOURCE_DIR, sorted_files)

    if not args.yes:
        print("\n=== 预览模式 ===")
        success, message = engine.preview(mappings, save_to_file=True)
        print(f"\n{message}")
        print("\n提示: 添加 --yes 参数以实际执行重命名")
        return 0

    success, message, count = engine.apply(mappings, confirmed=True)

    if success:
        print(f"\n{message}")
        return 0
    else:
        print(f"\n错误: {message}")
        return 1


def _handle_undo(args, engine: RenameEngine) -> int:
    """
    处理 undo 子命令。

    Args:
        args: 解析后的参数
        engine: 重命名引擎实例

    Returns:
        退出码
    """
    if not args.yes:
        print("提示: 添加 --yes 参数以实际执行撤销")
        print("注意: 撤销操作将根据上次执行的日志文件恢复文件名")
        return 0

    success, message, count = engine.undo(confirmed=True)

    if success:
        print(f"\n{message}")
        return 0
    else:
        print(f"\n错误: {message}")
        return 1


def _parse_extensions(ext_str: Optional[str]) -> Optional[List[str]]:
    """
    解析扩展名字符串。

    Args:
        ext_str: 逗号分隔的扩展名字符串

    Returns:
        扩展名列表，为空则返回 None
    """
    if not ext_str:
        return None

    extensions = [e.strip().lstrip(".") for e in ext_str.split(",")]
    return [e for e in extensions if e]


if __name__ == "__main__":
    sys.exit(main())
