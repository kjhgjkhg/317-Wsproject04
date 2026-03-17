"""Main entry point for the batch file renaming tool."""
import sys

from cli_parser import parse_args
from core_renamer import create_renamer_from_args
from rename_engine import RenameEngine
from utils.validators import validate_all_args, validate_extensions
from utils.helpers import get_files_from_source
from utils.config import EXIT_SUCCESS, EXIT_ERROR


def main() -> int:
    args = parse_args()
    
    if not args.command:
        print("ERROR: No command specified. Use --help for usage information.")
        return EXIT_ERROR
    
    if args.command == "undo":
        engine = RenameEngine()
        try:
            success = engine.undo()
            return EXIT_SUCCESS if success else EXIT_ERROR
        except Exception as e:
            print(f"Unexpected error during undo: {e}")
            return EXIT_ERROR
    
    is_valid, errors = validate_all_args(args)
    if not is_valid:
        print("ERROR: Invalid arguments:")
        for error in errors:
            print(f"  - {error}")
        return EXIT_ERROR
    
    try:
        _, _, extensions = validate_extensions(getattr(args, 'ext', None))
        files = get_files_from_source(extensions if extensions else None)
        
        if not files:
            print("No files found matching the criteria.")
            return EXIT_SUCCESS
        
        renamer = create_renamer_from_args(args)
        mappings = renamer.generate_mappings(files)
        
        engine = RenameEngine()
        
        if args.command == "preview":
            engine.preview(mappings)
            return EXIT_SUCCESS
        
        elif args.command == "apply":
            confirmed = getattr(args, 'yes', False)
            success = engine.apply(mappings, confirmed)
            return EXIT_SUCCESS if success else EXIT_ERROR
        
        else:
            print(f"Unknown command: {args.command}")
            return EXIT_ERROR
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return EXIT_ERROR
    except Exception as e:
        print(f"Unexpected error: {e}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
