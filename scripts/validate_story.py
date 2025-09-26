#!/usr/bin/env python

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

class StoryValidator:
    REQUIRED_SECTIONS = [
        "Status",
        "Story",
        "Acceptance Criteria",
        "Tasks/Subtasks",
        "Dev Notes",
        "Change Log",
        "Dev Agent Record",
        "QA Results"
    ]

    VALID_STATUSES = [
        "🟡 In Progress",
        "✅ Approved",
        "🔄 Pending Review",
        "🔄 Ready for Review",
        "❌ Rejected",
        "✅ Done"
    ]

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self._read_file()
        self.errors: List[str] = []

    def _read_file(self) -> str:
        """Read the story document file."""
        try:
            return self.file_path.read_text()
        except Exception as e:
            raise ValueError(f"Failed to read file {self.file_path}: {e}")

    def validate_sections(self) -> bool:
        """Validate that all required sections are present."""
        for section in self.REQUIRED_SECTIONS:
            pattern = f"## {section}"
            if pattern not in self.content:
                self.errors.append(f"Missing required section: {section}")
        return len(self.errors) == 0

    def validate_story_format(self) -> bool:
        """Validate the user story format."""
        story_patterns = [
            r"\*\*As a\*\* .+",
            r"\*\*I want\*\* .+",
            r"\*\*so that\*\* .+"
        ]
        for pattern in story_patterns:
            if not re.search(pattern, self.content):
                self.errors.append(f"Invalid story format: missing or incorrect {pattern}")
        return len(self.errors) == 0

    def validate_status(self) -> bool:
        """Validate the story status."""
        status_line = re.search(r"## Status\n(.+)", self.content)
        if not status_line:
            self.errors.append("Status section not found or incorrectly formatted")
            return False
        status = status_line.group(1).strip()
        if status not in self.VALID_STATUSES:
            self.errors.append(f"Invalid status: {status}")
            return False
        return True

    def validate_changelog(self) -> bool:
        """Validate the changelog format."""
        if "| Date | Version | Description | Author |" not in self.content:
            self.errors.append("Changelog table header missing or incorrect")
            return False
        if "|------|---------|-------------|---------|" not in self.content:
            self.errors.append("Changelog table format incorrect")
            return False
        return True

    def validate_markdown_formatting(self) -> bool:
        """Validate basic markdown formatting."""
        # Check header hierarchy
        headers = re.findall(r"^(#{1,6}) ", self.content, re.MULTILINE)
        current_level = 1
        for header in headers:
            level = len(header)
            if level - current_level > 1:
                self.errors.append(f"Invalid header hierarchy: jumping from H{current_level} to H{level}")
            current_level = level

        # Check code block formatting
        code_blocks = re.findall(r"```[a-z]*\n.*?```", self.content, re.DOTALL)
        for block in code_blocks:
            if not block.startswith("```") or not block.endswith("```"):
                self.errors.append("Invalid code block formatting")

        return len(self.errors) == 0

    def validate(self) -> bool:
        """Run all validations."""
        results = [
            self.validate_sections(),
            self.validate_story_format(),
            self.validate_status(),
            self.validate_changelog(),
            self.validate_markdown_formatting()
        ]
        return all(results)

    def get_errors(self) -> List[str]:
        """Get all validation errors."""
        return self.errors

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_story.py <story_file>")
        sys.exit(1)

    story_file = sys.argv[1]
    validator = StoryValidator(story_file)

    try:
        is_valid = validator.validate()
        if not is_valid:
            print("❌ Story document validation failed:")
            for error in validator.get_errors():
                print(f"  - {error}")
            sys.exit(1)
        print("✅ Story document validation passed")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
