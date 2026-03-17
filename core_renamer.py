"""Core renaming logic for generating new filenames based on rules."""
import re
from typing import List, Tuple, Dict, Any, Optional

from utils.helpers import split_name_ext, join_name_ext, get_file_mtime


class Renamer:
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        self._counter: Optional[int] = None
    
    def _apply_prefix(self, name: str) -> str:
        prefix = self.rules.get("prefix")
        if prefix:
            return f"{prefix}{name}"
        return name
    
    def _apply_suffix(self, name: str) -> str:
        suffix = self.rules.get("suffix")
        if suffix:
            return f"{name}{suffix}"
        return name
    
    def _apply_replace(self, name: str) -> str:
        replace_rule = self.rules.get("replace")
        if replace_rule:
            old_str, new_str = replace_rule
            return name.replace(old_str, new_str)
        return name
    
    def _apply_regex(self, name: str) -> str:
        regex_rule = self.rules.get("regex")
        if regex_rule:
            pattern, replacement = regex_rule
            try:
                return re.sub(pattern, replacement, name)
            except re.error:
                pass
        return name
    
    def _apply_date(self, name: str, filename: str) -> str:
        date_format = self.rules.get("date_format")
        if date_format:
            mtime = get_file_mtime(filename)
            if mtime:
                try:
                    date_str = mtime.strftime(date_format)
                    return f"{name}_{date_str}"
                except (ValueError, TypeError):
                    pass
        return name
    
    def _apply_numbering(self, name: str) -> str:
        number_start = self.rules.get("number_start")
        if number_start is not None:
            padding = self.rules.get("padding", 3)
            if self._counter is None:
                self._counter = number_start
            num_str = str(self._counter).zfill(padding)
            self._counter += 1
            return f"{name}_{num_str}"
        return name
    
    def generate_new_name(self, filename: str) -> str:
        name, ext = split_name_ext(filename)
        
        name = self._apply_replace(name)
        name = self._apply_regex(name)
        name = self._apply_date(name, filename)
        name = self._apply_numbering(name)
        name = self._apply_prefix(name)
        name = self._apply_suffix(name)
        
        return join_name_ext(name, ext)
    
    def generate_mappings(self, files: List[str]) -> List[Tuple[str, str]]:
        self._counter = None
        mappings = []
        for filename in files:
            new_name = self.generate_new_name(filename)
            mappings.append((filename, new_name))
        return mappings


def create_renamer_from_args(args) -> Renamer:
    rules: Dict[str, Any] = {}
    
    if hasattr(args, 'prefix') and args.prefix:
        rules["prefix"] = args.prefix
    if hasattr(args, 'suffix') and args.suffix:
        rules["suffix"] = args.suffix
    if hasattr(args, 'replace') and args.replace:
        parts = args.replace.split(",", 1)
        if len(parts) == 2:
            rules["replace"] = (parts[0], parts[1])
    if hasattr(args, 'regex') and args.regex:
        parts = args.regex.split(",", 1)
        if len(parts) == 2:
            rules["regex"] = (parts[0], parts[1])
    if hasattr(args, 'number_start') and args.number_start is not None:
        rules["number_start"] = args.number_start
        if hasattr(args, 'padding'):
            rules["padding"] = args.padding
    if hasattr(args, 'date_format') and args.date_format:
        rules["date_format"] = args.date_format
    
    return Renamer(rules)
