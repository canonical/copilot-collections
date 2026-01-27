#!/usr/bin/env python3
"""
Test glob patterns against repository files.

This script helps validate glob patterns used in path-specific instructions
by showing which files in the repository match the pattern.

Usage:
    python test_glob_pattern.py --pattern "**/*.py"
    python test_glob_pattern.py --pattern "src/components/**/*.tsx" --limit 50
    python test_glob_pattern.py --pattern "tests/**/*_test.go" --directory /path/to/repo
"""

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import List, Set


def find_matching_files(
    root_dir: Path,
    pattern: str,
    limit: int = 20,
    exclude_dirs: Set[str] = None
) -> List[Path]:
    """
    Find files matching the glob pattern.
    
    Args:
        root_dir: Root directory to search from
        pattern: Glob pattern to match (e.g., "**/*.py")
        limit: Maximum number of files to return (0 for unlimited)
        exclude_dirs: Set of directory names to exclude (e.g., {'.git', 'node_modules'})
    
    Returns:
        List of Path objects matching the pattern
    """
    if exclude_dirs is None:
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
    
    matches = []
    
    # Use pathlib's glob for simple patterns, otherwise walk manually for better control
    try:
        # Try using pathlib.glob first
        for path in root_dir.glob(pattern):
            if path.is_file():
                # Check if any parent directory should be excluded
                if not any(excluded in path.parts for excluded in exclude_dirs):
                    matches.append(path)
                    if limit > 0 and len(matches) >= limit:
                        break
    except Exception:
        # Fall back to manual walk with fnmatch
        for path in root_dir.rglob('*'):
            if path.is_file():
                # Skip excluded directories
                if any(excluded in path.parts for excluded in exclude_dirs):
                    continue
                
                # Get relative path for matching
                try:
                    rel_path = path.relative_to(root_dir)
                    if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(str(rel_path), pattern.replace('**/', '')):
                        matches.append(path)
                        if limit > 0 and len(matches) >= limit:
                            break
                except ValueError:
                    continue
    
    return sorted(matches)


def format_file_list(files: List[Path], root_dir: Path, show_full_paths: bool = False) -> str:
    """
    Format the list of files for display.
    
    Args:
        files: List of Path objects
        root_dir: Root directory for relative paths
        show_full_paths: Whether to show full paths or relative paths
    
    Returns:
        Formatted string with file list
    """
    if not files:
        return "No files matched the pattern."
    
    output_lines = []
    for idx, file_path in enumerate(files, 1):
        if show_full_paths:
            output_lines.append(f"  {idx:3d}. {file_path}")
        else:
            try:
                rel_path = file_path.relative_to(root_dir)
                output_lines.append(f"  {idx:3d}. {rel_path}")
            except ValueError:
                output_lines.append(f"  {idx:3d}. {file_path}")
    
    return "\n".join(output_lines)


def validate_directory(dir_path: str) -> Path:
    """
    Validate that the directory exists and is accessible.
    
    Args:
        dir_path: Directory path string
    
    Returns:
        Path object
    
    Raises:
        argparse.ArgumentTypeError: If directory is invalid
    """
    path = Path(dir_path).resolve()
    
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Directory does not exist: {dir_path}")
    
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"Not a directory: {dir_path}")
    
    return path


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Test glob patterns against repository files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pattern "**/*.py"
  %(prog)s --pattern "src/components/**/*.tsx" --limit 50
  %(prog)s --pattern "tests/**/*_test.go" --directory /path/to/repo
  %(prog)s --pattern "**/*.{yaml,yml}" --limit 0  # Show all matches

Common glob patterns:
  **/*.py           - All Python files recursively
  src/**/*.ts       - TypeScript files under src/
  tests/**/*_test.* - Test files with _test suffix
  *.md              - Markdown files in root only
  **/*.{js,jsx}     - JavaScript files (both extensions)
        """
    )
    
    parser.add_argument(
        '-p', '--pattern',
        required=True,
        help='Glob pattern to test (e.g., "**/*.py", "src/**/*.tsx")'
    )
    
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=20,
        help='Maximum number of files to display (default: 20, 0 for unlimited)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=validate_directory,
        default=Path.cwd(),
        help='Directory to search (default: current directory)'
    )
    
    parser.add_argument(
        '--full-paths',
        action='store_true',
        help='Show full paths instead of relative paths'
    )
    
    parser.add_argument(
        '--include-hidden',
        action='store_true',
        help='Include hidden directories (still excludes .git, node_modules, etc.)'
    )
    
    args = parser.parse_args()
    
    # Configure exclusions
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
    if args.include_hidden:
        # Still exclude common development directories
        exclude_dirs = {'.git', 'node_modules', '__pycache__'}
    
    # Print search information
    print(f"Searching in: {args.directory}")
    print(f"Pattern: {args.pattern}")
    print(f"Limit: {'unlimited' if args.limit == 0 else args.limit}")
    print()
    
    # Find matching files
    try:
        matches = find_matching_files(
            root_dir=args.directory,
            pattern=args.pattern,
            limit=args.limit,
            exclude_dirs=exclude_dirs
        )
    except Exception as e:
        print(f"Error searching for files: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Display results
    total_matches = len(matches)
    
    if total_matches == 0:
        print("❌ No files matched the pattern.")
        print("\nTips:")
        print("  - Check if the pattern syntax is correct")
        print("  - Verify files exist in the specified directory")
        print("  - Try a broader pattern (e.g., '**/*.py' instead of 'src/**/*.py')")
        sys.exit(0)
    
    print(f"✅ Found {total_matches} matching file{'s' if total_matches != 1 else ''}:")
    print()
    print(format_file_list(matches, args.directory, args.full_paths))
    
    if args.limit > 0 and total_matches >= args.limit:
        print()
        print(f"⚠️  Results limited to {args.limit} files. Use --limit 0 to see all matches.")
    
    # Print summary
    print()
    print("=" * 60)
    print(f"Total matches: {total_matches}")
    
    # Provide feedback on scope size
    if total_matches < 10:
        print("💡 Scope: Small - Consider using global instructions or inline comments")
    elif total_matches <= 500:
        print("✅ Scope: Good - This is a good candidate for path-specific instructions")
    else:
        print("⚠️  Scope: Large - Consider splitting into more specific patterns")


if __name__ == "__main__":
    main()
