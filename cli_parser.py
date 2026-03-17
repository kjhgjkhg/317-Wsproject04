"""Command-line argument parser for the batch file renaming tool."""
import argparse
from typing import Any
from argparse import Namespace

from utils.config import DEFAULT_PADDING


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rename",
        description="Batch file renaming tool with multiple naming rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rename preview --prefix "IMG_" --ext jpg,png
  rename apply --replace "old,new" --yes
  rename undo
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    preview_parser = subparsers.add_parser("preview", help="Preview renaming effect (no actual changes)")
    _add_common_arguments(preview_parser)
    
    apply_parser = subparsers.add_parser("apply", help="Apply the renaming operation")
    _add_common_arguments(apply_parser)
    apply_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Confirm the operation (required for actual renaming)"
    )
    
    undo_parser = subparsers.add_parser("undo", help="Undo the last renaming operation")
    
    return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--prefix", "-p",
        type=str,
        default=None,
        help="Add prefix to filenames"
    )
    parser.add_argument(
        "--suffix", "-s",
        type=str,
        default=None,
        help="Add suffix to filenames (before extension)"
    )
    parser.add_argument(
        "--replace", "-r",
        type=str,
        default=None,
        help="String replacement: 'old,new'"
    )
    parser.add_argument(
        "--number-start", "-n",
        type=int,
        default=None,
        help="Start number for sequential naming"
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=DEFAULT_PADDING,
        help=f"Zero padding for sequential numbers (default: {DEFAULT_PADDING})"
    )
    parser.add_argument(
        "--date-format", "-d",
        type=str,
        default=None,
        help="Date format using file modification time (e.g., '%%Y%%m%%d')"
    )
    parser.add_argument(
        "--regex", "-x",
        type=str,
        default=None,
        help="Regex replacement: 'pattern,replacement'"
    )
    parser.add_argument(
        "--ext", "-e",
        type=str,
        default=None,
        help="Comma-separated list of file extensions to process"
    )


def parse_args(args_list=None) -> Namespace:
    parser = create_parser()
    return parser.parse_args(args_list)
