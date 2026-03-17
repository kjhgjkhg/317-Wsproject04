"""File system operations and conflict detection for the renaming engine."""
import os
from typing import List, Tuple, Dict, Set

from utils.config import SOURCE_DIR
from utils.helpers import format_as_table, save_preview, save_log, load_log
from utils.validators import is_protected_file


class RenameEngine:
    def __init__(self):
        self._conflicts: List[Tuple[str, str]] = []
    
    def check_conflicts(self, mappings: List[Tuple[str, str]]) -> bool:
        self._conflicts = []
        existing_files: Set[str] = set()
        
        try:
            for entry in os.listdir(SOURCE_DIR):
                if os.path.isfile(os.path.join(SOURCE_DIR, entry)):
                    existing_files.add(entry.lower())
        except (OSError, IOError):
            pass
        
        new_names: Dict[str, str] = {}
        for old_name, new_name in mappings:
            new_name_lower = new_name.lower()
            if new_name_lower in new_names:
                self._conflicts.append((old_name, f"Duplicate target: '{new_name}' (also used by '{new_names[new_name_lower]}')"))
            elif new_name_lower in existing_files and new_name_lower != old_name.lower():
                self._conflicts.append((old_name, f"Target file exists: '{new_name}'"))
            new_names[new_name_lower] = old_name
        
        return len(self._conflicts) == 0
    
    def get_conflicts(self) -> List[Tuple[str, str]]:
        return self._conflicts
    
    def preview(self, mappings: List[Tuple[str, str]]) -> bool:
        print("\n=== Rename Preview ===")
        print()
        
        if not mappings:
            print("No files found matching the criteria.")
            return True
        
        print(format_as_table(mappings))
        
        if not self.check_conflicts(mappings):
            print("WARNING: Conflicts detected!")
            for old_name, msg in self._conflicts:
                print(f"  - {old_name}: {msg}")
            print()
        
        if save_preview(mappings):
            from utils.config import PREVIEW_FILE
            print(f"Preview saved to: {PREVIEW_FILE}")
        
        return True
    
    def apply(self, mappings: List[Tuple[str, str]], confirmed: bool = False) -> bool:
        if not confirmed:
            print("ERROR: Use --yes flag to confirm the renaming operation.")
            print("Use 'rename preview' to see the changes first.")
            return False
        
        if not mappings:
            print("No files to process.")
            return True
        
        if not self.check_conflicts(mappings):
            print("ERROR: Cannot apply - conflicts detected!")
            for old_name, msg in self._conflicts:
                print(f"  - {old_name}: {msg}")
            return False
        
        operations: Dict[str, str] = {}
        success_count = 0
        error_count = 0
        
        print("\nApplying renaming operations...")
        print()
        
        for old_name, new_name in mappings:
            old_path = os.path.join(SOURCE_DIR, old_name)
            new_path = os.path.join(SOURCE_DIR, new_name)
            
            if is_protected_file(old_name) or is_protected_file(new_name):
                print(f"SKIP: {old_name} -> {new_name} (protected file)")
                continue
            
            try:
                os.rename(old_path, new_path)
                operations[old_name] = new_name
                success_count += 1
                print(f"OK: {old_name} -> {new_name}")
            except (OSError, IOError) as e:
                error_count += 1
                print(f"FAIL: {old_name} -> {new_name} ({e})")
        
        print()
        print(f"Summary: {success_count} succeeded, {error_count} failed")
        
        if operations:
            save_log(operations)
            from utils.config import LOG_FILE
            print(f"Log saved to: {LOG_FILE}")
        
        return error_count == 0
    
    def undo(self) -> bool:
        operations = load_log()
        if operations is None:
            return False
        
        if not operations:
            print("No operations found in log.")
            return True
        
        print("Undoing last rename operation...")
        print()
        
        reversed_ops = [(new_name, old_name) for old_name, new_name in operations.items()]
        
        success_count = 0
        error_count = 0
        
        for new_name, old_name in reversed_ops:
            old_path = os.path.join(SOURCE_DIR, new_name)
            new_path = os.path.join(SOURCE_DIR, old_name)
            
            if not os.path.exists(old_path):
                print(f"SKIP: {new_name} -> {old_name} (source not found)")
                continue
            
            if os.path.exists(new_path):
                print(f"SKIP: {new_name} -> {old_name} (target already exists)")
                continue
            
            try:
                os.rename(old_path, new_path)
                success_count += 1
                print(f"OK: {new_name} -> {old_name}")
            except (OSError, IOError) as e:
                error_count += 1
                print(f"FAIL: {new_name} -> {old_name} ({e})")
        
        print()
        print(f"Summary: {success_count} succeeded, {error_count} failed")
        
        return error_count == 0
