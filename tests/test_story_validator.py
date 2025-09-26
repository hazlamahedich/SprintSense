import pytest
from pathlib import Path
from scripts.validate_story import StoryValidator

@pytest.fixture
def valid_story_content():
    return """# Story 1.1: Test Story

## Status
🟡 In Progress

Story Points: TBD
Sprint: TBD

## Story
**As a** developer
**I want** to test story validation
**so that** I can ensure document quality

## Acceptance Criteria
1. [ ] First criterion
2. [ ] Second criterion

## Tasks/Subtasks
- [ ] Task 1
  - [ ] Subtask 1.1
- [ ] Task 2

## Dev Notes
Test notes

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-09-26 | 1.0 | Initial creation | Test Author |

## Dev Agent Record
Test record

## QA Results
Test results
"""

@pytest.fixture
def temp_story_file(tmp_path: Path, valid_story_content: str):
    story_file = tmp_path / "test_story.md"
    story_file.write_text(valid_story_content)
    return story_file

def test_validate_sections_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate_sections()
    assert not validator.get_errors()

def test_validate_sections_failure(tmp_path):
    invalid_content = "# Invalid Story\n\nNo sections"
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate_sections()
    errors = validator.get_errors()
    assert len(errors) == len(StoryValidator.REQUIRED_SECTIONS)

def test_validate_story_format_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate_story_format()
    assert not validator.get_errors()

def test_validate_story_format_failure(tmp_path):
    invalid_content = """# Invalid Story

## Story
As a user
I want something
So that benefit
"""
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate_story_format()
    assert len(validator.get_errors()) == 3

def test_validate_status_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate_status()
    assert not validator.get_errors()

def test_validate_status_failure(tmp_path):
    invalid_content = """# Invalid Story
## Status
Invalid Status
"""
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate_status()
    assert len(validator.get_errors()) == 1

def test_validate_changelog_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate_changelog()
    assert not validator.get_errors()

def test_validate_changelog_failure(tmp_path):
    invalid_content = """# Invalid Story
## Change Log
Invalid changelog
"""
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate_changelog()
    assert len(validator.get_errors()) == 1

def test_validate_markdown_formatting_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate_markdown_formatting()
    assert not validator.get_errors()

def test_validate_markdown_formatting_failure(tmp_path):
    invalid_content = """# Header 1
### Invalid Header Jump
```
Unclosed code block
"""
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate_markdown_formatting()
    assert len(validator.get_errors()) > 0

def test_validate_full_document_success(temp_story_file):
    validator = StoryValidator(str(temp_story_file))
    assert validator.validate()
    assert not validator.get_errors()

def test_validate_full_document_failure(tmp_path):
    invalid_content = "# Invalid Story"
    story_file = tmp_path / "invalid_story.md"
    story_file.write_text(invalid_content)

    validator = StoryValidator(str(story_file))
    assert not validator.validate()
    assert len(validator.get_errors()) > 0

def test_nonexistent_file():
    with pytest.raises(ValueError):
        StoryValidator("/nonexistent/file.md")
