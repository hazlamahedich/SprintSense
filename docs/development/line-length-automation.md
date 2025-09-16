# Line Length Automation

This document explains how SprintSense automatically handles E501 line length errors to prevent CI failures.

## Overview

Line length errors (E501) occur when code lines exceed the configured maximum length
(88 characters). Our automation system catches and fixes these issues at multiple levels.

## Automated Prevention & Fixing

### 1. Real-time Prevention (VS Code)

**Visual Indicators:**

- Ruler lines at 88 and 100 characters
- Word wrap at 88 characters for guidance
- Real-time linting with Error Lens extension

**Auto-formatting:**

- Black formatter respects 88-character limit
- Format-on-save automatically reformats long lines
- Automatic line breaking for imports and strings

### 2. Pre-commit Hooks (Automatic)

**Line Length Fixer Hook:**

```yaml
- id: fix-line-lengths
  name: Fix line lengths (backend)
  entry: python3 scripts/fix-line-lengths.py
  language: system
  files: ^backend/.*\.py$
```

**What it fixes automatically:**

- Long f-strings → Multi-line f-strings
- Long function calls → Multi-line arguments
- Long return statements → Parenthesized expressions
- Long expressions → Logical line breaks

**AutoPEP8 Hook:**

- Automatic PEP8 compliance including line length
- Aggressive mode for comprehensive fixes
- Respects Black formatter compatibility

### 3. Manual Commands

**Fix specific files:**

```bash
python3 scripts/fix-line-lengths.py backend/app/file.py
```

**Fix all Python files:**

```bash
make fix-line-lengths
```

**Fix all issues including line lengths:**

```bash
make fix
```

## Line Breaking Strategies

### 1. Long Strings

**Before (E501 error):**

```python
return f"<TeamMember(id={self.id}, team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"
```

**After (automatic fix):**

```python
return (
    f"<TeamMember(id={self.id}, team_id={self.team_id}, "
    f"user_id={self.user_id}, role={self.role})>"
)
```

### 2. Function Calls

**Before:**

```python
some_function(very_long_argument, another_very_long_argument, third_argument)
```

**After:**

```python
some_function(
    very_long_argument,
    another_very_long_argument,
    third_argument
)
```

### 3. Complex Expressions

**Before:**

```python
result = some_object.method().another_method(arg1, arg2).final_method(arg3, arg4)
```

**After:**

```python
result = (
    some_object.method()
    .another_method(arg1, arg2)
    .final_method(arg3, arg4)
)
```

## Configuration

### Flake8 Configuration

```yaml
args: [
  "--max-line-length=88",
  "--extend-ignore=E203,W503"  # E501 NOT ignored anymore
]
```

### Black Configuration

```python
"python.formatting.blackArgs": ["--line-length=88"]
```

### VS Code Settings

```json
{
  "editor.rulers": [88, 100],
  "editor.wordWrap": "wordWrapColumn",
  "editor.wordWrapColumn": 88
}
```

## Testing the System

### Create a test file with long lines

```python
# test_long_lines.py
def test_function():
    return f"This is a very long line that definitely exceeds the 88 character limit and should be caught by our automation"
```

### Run the automation

```bash
make fix-line-lengths
```

### Verify the fix

```bash
make backend-lint
```

## Integration Points

### 1. Git Workflow

- **Pre-commit:** Automatically fixes lines before commit
- **Pre-push:** Validates no E501 errors remain
- **CI Pipeline:** Should never see E501 errors

### 2. Development Workflow

- **VS Code:** Real-time visual feedback
- **File watcher:** Fixes issues as you save
- **Manual fixes:** Available for complex cases

### 3. Team Workflow

- **Consistent standards:** All developers get same fixes
- **Automatic resolution:** No manual intervention needed
- **Clear feedback:** Shows what was fixed and where

## Common Scenarios

### 1. Model **repr** methods

```python
# Long model representations are automatically broken
def __repr__(self) -> str:
    return (
        f"<{self.__class__.__name__}(id={self.id}, "
        f"name={self.name}, status={self.status})>"
    )
```

### 2. Long SQL queries

```python
# Long queries are broken at logical points
query = (
    "SELECT * FROM users "
    "WHERE created_at > %s AND status = %s "
    "ORDER BY created_at DESC"
)
```

### 3. Complex validations

```python
# Long conditionals are wrapped
if (
    condition_one and condition_two 
    and condition_three and condition_four
):
    do_something()
```

## Troubleshooting

### If automation doesn't fix a line

1. **Check syntax:** Ensure the line is valid Python
2. **Manual fix:** Some complex cases need human intervention
3. **Report pattern:** Add new patterns to the fixer script

### Common manual fixes needed

- Complex regex patterns
- Deeply nested expressions
- Comments that are too long
- Docstrings (handled by docstring formatters)

### VS Code not showing rulers

1. Check settings.json is applied
2. Restart VS Code
3. Ensure Python extension is active

## Benefits

### Automated Prevention

- ✅ Catches issues before they reach CI
- ✅ Consistent code style across team
- ✅ Reduces code review noise
- ✅ Prevents deployment pipeline failures

### Developer Experience

- ✅ No manual line counting
- ✅ Intelligent break points
- ✅ Preserves code readability  
- ✅ Works with existing tools (Black, isort)

### Maintenance

- ✅ Self-healing codebase
- ✅ Automatic updates via pre-commit
- ✅ Extensible for new patterns
- ✅ Clear audit trail of changes

This system ensures that E501 line length errors are caught and fixed automatically at
every stage of development, preventing CI failures and maintaining consistent code quality.
