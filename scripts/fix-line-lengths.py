#!/usr/bin/env python3
"""
SprintSense Line Length Fixer
Automatically fixes E501 line length errors in Python files.
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import List, Tuple


class LineLengthFixer:
    """Fixes line length issues in Python files."""

    def __init__(self, max_length: int = 88):
        self.max_length = max_length
        self.fixes_applied = 0

    def fix_long_strings(self, line: str, indent: str = "") -> List[str]:
        """Fix long string literals by breaking them into multiple lines."""
        # Handle f-strings and regular strings
        string_patterns = [
            (r'f"([^"]*)"', 'f"{}"\n{}f"{}"'),
            (r"f'([^']*)'", "f'{}'\n{}f'{}'"),
            (r'"([^"]*)"', '"{}"\n{}"{}"'),
            (r"'([^']*)'", "'{}'\n{}'{}'"),
        ]

        for pattern, replacement in string_patterns:
            if re.search(pattern, line) and len(line) > self.max_length:
                # Find a good break point (space, comma, etc.)
                break_point = self.max_length - len(indent) - 10
                match = re.search(pattern, line)
                if match:
                    content = match.group(1)
                    if len(content) > break_point:
                        # Split at word boundaries
                        words = content.split(" ")
                        lines = []
                        current_line = ""

                        for word in words:
                            if len(current_line + word) < break_point:
                                current_line += (" " if current_line else "") + word
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = word

                        if current_line:
                            lines.append(current_line)

                        if len(lines) > 1:
                            # Create multiline string
                            if 'f"' in line or "f'" in line:
                                # F-string
                                result = []
                                for i, part in enumerate(lines):
                                    if i == 0:
                                        result.append(line.replace(content, part))
                                    else:
                                        result.append(f'{indent}f"{part}"')
                                return result
                            else:
                                # Regular string - use parentheses for concatenation
                                result = []
                                for i, part in enumerate(lines):
                                    if i == 0:
                                        new_line = line.replace(
                                            (
                                                f'"{content}"'
                                                if '"' in line
                                                else f"'{content}'"
                                            ),
                                            f'("{part}"',
                                        )
                                        result.append(new_line)
                                    elif i == len(lines) - 1:
                                        result.append(f'{indent}"{part}")')
                                    else:
                                        result.append(f'{indent}"{part}"')
                                return result

        return [line]

    def fix_long_expressions(self, line: str, indent: str = "") -> List[str]:
        """Fix long expressions by breaking them at logical points."""
        # Look for function calls with multiple arguments
        if "(" in line and ")" in line and len(line) > self.max_length:
            # Find function calls with multiple arguments
            func_call_pattern = r"(\w+\([^)]+\))"
            match = re.search(func_call_pattern, line)

            if match and "," in match.group(1):
                # Break at commas
                before_call = line[: match.start(1)]
                call_content = match.group(1)
                after_call = line[match.end(1) :]

                # Extract function name and arguments
                func_name = call_content.split("(")[0]
                args_part = call_content[len(func_name) + 1 : -1]
                args = [arg.strip() for arg in args_part.split(",")]

                if len(args) > 1:
                    result = [f"{before_call}{func_name}("]
                    for i, arg in enumerate(args):
                        if i == len(args) - 1:
                            result.append(f"{indent}    {arg}")
                        else:
                            result.append(f"{indent}    {arg},")
                    result.append(f"{indent}){after_call}")
                    return result

        # Look for long return statements with f-strings
        if line.strip().startswith('return f"') and len(line) > self.max_length:
            indent_match = re.match(r"^(\s*)", line)
            current_indent = indent_match.group(1) if indent_match else ""

            # Extract the f-string content
            f_string_match = re.search(r'return f"([^"]*)"', line)
            if f_string_match:
                content = f_string_match.group(1)

                # Find good break points (after commas, spaces)
                break_points = []
                for i, char in enumerate(content):
                    if char in [",", " "] and i < len(content) - 1:
                        break_points.append(i + 1)

                # Find the best break point
                target_length = (
                    self.max_length - len(current_indent) - 15
                )  # Account for "return (" and quotes
                best_break = None
                for bp in break_points:
                    if bp <= target_length:
                        best_break = bp

                if best_break:
                    part1 = content[:best_break].rstrip()
                    part2 = content[best_break:].lstrip()

                    return [
                        f"{current_indent}return (",
                        f'{current_indent}    f"{part1} "',
                        f'{current_indent}    f"{part2}"',
                        f"{current_indent})",
                    ]

        return [line]

    def fix_line(self, line: str, line_number: int) -> List[str]:
        """Fix a single line if it's too long."""
        if len(line) <= self.max_length:
            return [line]

        # Get indentation
        indent_match = re.match(r"^(\s*)", line)
        indent = indent_match.group(1) if indent_match else ""

        # Try different fixing strategies

        # 1. Fix long strings
        result = self.fix_long_strings(line, indent)
        if len(result) > 1:
            self.fixes_applied += 1
            return result

        # 2. Fix long expressions
        result = self.fix_long_expressions(line, indent)
        if len(result) > 1:
            self.fixes_applied += 1
            return result

        # 3. Generic line breaking at logical points
        if "," in line and len(line) > self.max_length:
            # Find the last comma before the max length
            for i in range(self.max_length, 0, -1):
                if i < len(line) and line[i] == ",":
                    part1 = line[: i + 1]
                    part2 = indent + "    " + line[i + 1 :].lstrip()
                    self.fixes_applied += 1
                    return [part1, part2]

        return [line]

    def fix_file(self, file_path: Path) -> bool:
        """Fix line length issues in a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            fixes_in_file = 0

            for line_num, line in enumerate(lines, 1):
                line = line.rstrip("\n\r")
                fixed_lines = self.fix_line(line, line_num)

                if len(fixed_lines) > 1:
                    fixes_in_file += 1
                    print(f"Fixed long line {line_num} in {file_path}")

                new_lines.extend([line + "\n" for line in fixed_lines])

            if fixes_in_file > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print(f"Applied {fixes_in_file} fixes to {file_path}")
                return True

            return False

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Fix line length issues in Python files"
    )
    parser.add_argument("files", nargs="+", help="Python files to fix")
    parser.add_argument(
        "--max-length", type=int, default=88, help="Maximum line length (default: 88)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes",
    )

    args = parser.parse_args()

    fixer = LineLengthFixer(max_length=args.max_length)

    files_fixed = 0
    for file_path in args.files:
        path = Path(file_path)
        if path.suffix == ".py" and path.exists():
            if not args.dry_run:
                if fixer.fix_file(path):
                    files_fixed += 1
            else:
                print(f"Would check: {path}")

    print(
        f"\nSummary: {fixer.fixes_applied} line length issues fixed in {files_fixed} files"
    )

    if fixer.fixes_applied > 0:
        print(
            "\nNote: Please review the changes and run your tests to ensure correctness."
        )


if __name__ == "__main__":
    main()
