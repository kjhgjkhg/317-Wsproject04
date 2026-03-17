"""
rename_engine.py - 文件系统操作引擎模块

负责实际文件系统操作（os.rename）、冲突检测、预览生成。
"""

import os
import sys
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from utils.config import (
    SOURCE_DIR,
    OUTPUT_DIR,
    PROTECTED_FILE,
    ERROR_MESSAGES,
)
from utils.helpers import (
    get_files_in_directory,
    sort_files_by_mtime,
    save_preview,
    save_log,
    load_log,
    print_preview,
)
from utils.validators import (
    validate_source_directory,
    validate_output_directory,
    is_protected_file,
    check_multiple_conflicts,
)


class RenameEngine:
    """重命名引擎类。"""

    def __init__(self, source_dir: str = SOURCE_DIR, output_dir: str = OUTPUT_DIR):
        """
        初始化重命名引擎。

        Args:
            source_dir: 源文件目录
            output_dir: 输出目录
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self._last_mappings: List[Tuple[str, str]] = []

    def validate_directories(self) -> Tuple[bool, List[str]]:
        """
        校验目录是否有效。

        Returns:
            (是否有效, 错误消息列表)
        """
        errors: List[str] = []

        is_valid, error = validate_source_directory()
        if not is_valid:
            errors.append(error)

        is_valid, error = validate_output_directory()
        if not is_valid:
            errors.append(error)

        return len(errors) == 0, errors

    def get_target_files(
        self,
        extensions: Optional[List[str]] = None
    ) -> List[str]:
        """
        获取待处理的文件列表。

        Args:
            extensions: 扩展名过滤列表

        Returns:
            文件名列表
        """
        return get_files_in_directory(
            self.source_dir,
            extensions=extensions,
            include_protected=False
        )

    def preview(
        self,
        mappings: List[Tuple[str, str]],
        save_to_file: bool = True
    ) -> Tuple[bool, str]:
        """
        预览重命名结果。

        Args:
            mappings: (旧文件名, 新文件名) 元组列表
            save_to_file: 是否保存到文件

        Returns:
            (是否成功, 消息)
        """
        if not mappings:
            return False, ERROR_MESSAGES["no_files_found"]

        conflicts = check_multiple_conflicts(self.source_dir, mappings)
        if conflicts:
            print("\n检测到文件名冲突:")
            for old_name, msg in conflicts:
                print(f"  - {old_name}: {msg}")
            return False, "存在文件名冲突，请调整重命名规则"

        print("\n重命名预览:")
        print_preview(mappings)

        if save_to_file:
            output_path = save_preview(mappings, self.output_dir)
            print(f"\n{ERROR_MESSAGES['preview_saved'].format(path=output_path)}")

        self._last_mappings = mappings
        return True, f"共 {len(mappings)} 个文件待重命名"

    def apply(
        self,
        mappings: List[Tuple[str, str]],
        confirmed: bool = False
    ) -> Tuple[bool, str, int]:
        """
        执行重命名操作。

        Args:
            mappings: (旧文件名, 新文件名) 元组列表
            confirmed: 是否已确认执行

        Returns:
            (是否成功, 消息, 成功数量)
        """
        if not mappings:
            return False, ERROR_MESSAGES["no_files_found"], 0

        if not confirmed:
            print("\n请使用 --yes 参数确认执行重命名操作")
            print("提示: 先运行 preview 子命令查看预览效果")
            return False, "未确认执行", 0

        conflicts = check_multiple_conflicts(self.source_dir, mappings)
        if conflicts:
            print("\n检测到文件名冲突:")
            for old_name, msg in conflicts:
                print(f"  - {old_name}: {msg}")
            return False, "存在文件名冲突", 0

        success_count = 0
        failed_list: List[Tuple[str, str]] = []

        for old_name, new_name in mappings:
            if is_protected_file(old_name):
                print(f"跳过受保护文件: {old_name}")
                continue

            old_path = os.path.join(self.source_dir, old_name)
            new_path = os.path.join(self.source_dir, new_name)

            try:
                os.rename(old_path, new_path)
                success_count += 1
                print(f"重命名: {old_name} -> {new_name}")
            except PermissionError:
                failed_list.append((old_name, "权限不足"))
                print(f"失败: {old_name} - 权限不足")
            except FileNotFoundError:
                failed_list.append((old_name, "文件不存在"))
                print(f"失败: {old_name} - 文件不存在")
            except OSError as e:
                failed_list.append((old_name, str(e)))
                print(f"失败: {old_name} - {e}")

        extra_info = {
            "timestamp": datetime.now().isoformat(),
            "source_dir": self.source_dir,
            "success_count": success_count,
            "failed_count": len(failed_list),
        }

        if success_count > 0:
            log_path = save_log(mappings, self.output_dir, extra_info)
            print(f"\n{ERROR_MESSAGES['log_saved'].format(path=log_path)}")

        if failed_list:
            print(f"\n失败 {len(failed_list)} 个文件:")
            for name, reason in failed_list:
                print(f"  - {name}: {reason}")

        return True, f"成功重命名 {success_count} 个文件", success_count

    def undo(self, confirmed: bool = False) -> Tuple[bool, str, int]:
        """
        撤销上一次重命名操作。

        Args:
            confirmed: 是否已确认执行

        Returns:
            (是否成功, 消息, 成功数量)
        """
        if not confirmed:
            print("\n请使用 --yes 参数确认执行撤销操作")
            return False, "未确认执行", 0

        log_data = load_log(self.output_dir)
        if not log_data:
            return False, ERROR_MESSAGES["log_not_found"], 0

        renamed_files = log_data.get("renamed_files", [])
        if not renamed_files:
            return False, "日志文件中没有重命名记录", 0

        success_count = 0
        failed_list: List[Tuple[str, str]] = []

        for item in renamed_files:
            new_name = item.get("new")
            old_name = item.get("old")

            if not new_name or not old_name:
                continue

            new_path = os.path.join(self.source_dir, new_name)
            old_path = os.path.join(self.source_dir, old_name)

            try:
                if os.path.exists(new_path):
                    os.rename(new_path, old_path)
                    success_count += 1
                    print(f"撤销: {new_name} -> {old_name}")
                else:
                    print(f"跳过: {new_name} 文件不存在")
            except PermissionError:
                failed_list.append((new_name, "权限不足"))
                print(f"失败: {new_name} - 权限不足")
            except OSError as e:
                failed_list.append((new_name, str(e)))
                print(f"失败: {new_name} - {e}")

        if success_count > 0:
            undo_log_path = os.path.join(
                self.output_dir,
                f"undo_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                import json
                with open(undo_log_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "action": "undo",
                        "timestamp": datetime.now().isoformat(),
                        "success_count": success_count,
                        "original_log": log_data
                    }, f, ensure_ascii=False, indent=2)
            except IOError:
                pass

        print(f"\n{ERROR_MESSAGES['undo_success'].format(count=success_count)}")

        return True, ERROR_MESSAGES["undo_success"].format(count=success_count), success_count

    def get_sorted_files(self, filenames: List[str]) -> List[Tuple[str, float]]:
        """
        获取按修改时间排序的文件列表。

        Args:
            filenames: 文件名列表

        Returns:
            排序后的 (文件名, 修改时间) 元组列表
        """
        return sort_files_by_mtime(self.source_dir, filenames)
