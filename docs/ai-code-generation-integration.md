# AI Code Generation Integration Guide

## Overview

This guide explains how to integrate the [Coding Standards](./architecture/coding-standards.md) into your AI-assisted development workflow to **eliminate linting errors** and **reduce iteration cycles**.

## Quick Start

### For AI Agents (Dev Persona)
When generating code, **ALWAYS** reference these documents in order:
1. **[`docs/architecture/coding-standards.md`](./architecture/coding-standards.md)** - Complete linting rules and patterns
2. **[`claude_suggestions.md`](../claude_suggestions.md)** - Quality and creativity guidelines  
3. **Current story requirements** - Feature specifications

### Post-Generation Validation Workflow
```bash
# 1. Generate code following standards
# 2. Auto-format
cd frontend && npm run format  # Frontend
cd backend && poetry run black . && poetry run isort .  # Backend

# 3. Lint check  
cd frontend && npm run lint     # Frontend
cd backend && poetry run flake8 app/  # Backend

# 4. Type check
cd frontend && npm run build    # TypeScript check
cd backend && poetry run mypy app/  # Python type check

# 5. Only commit if ALL pass
```

## BMAD Integration

### Updated Dev Agent Workflow

The dev agent should now:

1. **On Activation**: Auto-load coding standards document
   ```yaml
   devLoadAlwaysFiles:
     - docs/architecture/coding-standards.md  # ← ADDED
     - docs/architecture/tech-stack.md
     - docs/architecture/source-tree.md
   ```

2. **Before Code Generation**: Review the **AI Generation Checklist** from coding standards

3. **After Code Generation**: Run the **Post-Generation Validation** steps above

4. **Before Story Completion**: Ensure **zero linting errors** across all modified files

### Story Template Updates

Add this section to user stories:

```markdown
## Code Quality Gate
- [ ] All linting rules pass (ESLint + flake8)
- [ ] All formatting applied (Prettier + Black)
- [ ] All type checking passes (TypeScript + mypy)
- [ ] Creative UI requirements met (if frontend)
- [ ] Security patterns followed
- [ ] Test coverage meets minimums
```

## Common Linting Errors & Fixes

### Frontend (TypeScript/React)

| Error | Fix | Rule |
|-------|-----|------|
| `'any' type` | Use specific interfaces | `@typescript-eslint/no-explicit-any` |
| `Missing dependencies` | Add to useEffect deps | `react-hooks/exhaustive-deps` |
| `Unused import` | Remove unused imports | `@typescript-eslint/no-unused-vars` |
| `Class component` | Convert to function component | `react/prefer-stateless-function` |

### Backend (Python/FastAPI)

| Error | Fix | Rule |
|-------|-----|------|
| `E501: Line too long` | Run `black .` | flake8 |
| `F401: Unused import` | Remove unused imports | flake8 |
| `Missing type annotation` | Add complete type hints | mypy |
| `Import order` | Run `isort .` | isort |

## Integration with GitHub Actions

Add this step to your CI pipeline:

```yaml
# .github/workflows/ci.yml
  lint-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Frontend linting
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install frontend deps
        run: cd frontend && npm ci
      - name: Lint frontend
        run: cd frontend && npm run lint && npm run format:check
        
      # Backend linting  
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install poetry
        run: pip install poetry
      - name: Install backend deps
        run: cd backend && poetry install
      - name: Lint backend
        run: cd backend && poetry run flake8 app/ && poetry run mypy app/
```

## VS Code Integration

Add these workspace settings:

```json
// .vscode/settings.json
{
  // Frontend
  "eslint.workingDirectories": ["frontend"],
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  
  // Backend
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.path": "isort"
}
```

## AI Prompt Templates

### For Code Generation

```markdown
**Context**: I'm working on SprintSense, a TypeScript/React frontend with Python/FastAPI backend.

**Requirements**: 
{feature requirements}

**Standards**: Follow the coding standards in `/docs/architecture/coding-standards.md`:
- Use function components with TypeScript
- Implement proper error handling
- Apply creative UI patterns (no generic designs)
- Use dependency injection
- Include complete type annotations
- Follow naming conventions

**Quality Gates**: Code must pass ESLint, Prettier, flake8, and mypy without errors.

**Task**: {specific task}
```

### For Code Review

```markdown
**Review this code against SprintSense coding standards**:

Checklist:
- [ ] Naming conventions followed
- [ ] Type annotations complete  
- [ ] Error handling implemented
- [ ] No anti-patterns present
- [ ] Linting would pass
- [ ] Creative requirements met (frontend)
- [ ] Security practices followed

Code:
{generated code}
```

## Monitoring & Metrics

Track these metrics to measure improvement:

- **Linting Error Rate**: Errors per PR before/after standards
- **PR Review Cycles**: Average rounds of feedback  
- **CI/CD Success Rate**: Percentage of builds passing linting
- **Creative Score**: Frontend components meeting 8/10+ creativity (manual review)

## Troubleshooting

### "Still getting linting errors"

1. **Verify standards document is loaded** in dev agent session
2. **Check rule coverage** - may need to update standards doc  
3. **Run emergency fix commands**:
   ```bash
   cd frontend && npm run lint:fix && npm run format
   cd backend && poetry run black . && poetry run isort .
   ```

### "AI not following creative requirements"

1. **Review claude_suggestions.md** - ensure creativity patterns are clear
2. **Check UI examples** - may need more specific examples
3. **Validate creativity score** manually before accepting

### "Type errors still occurring"

1. **Enable strict TypeScript** in frontend (already configured)
2. **Run mypy in strict mode** for backend (configured in pyproject.toml)
3. **Add missing type imports** explicitly

## Next Steps

1. **Update dev agent config** with new `devLoadAlwaysFiles` entry
2. **Test on a sample story** to validate the workflow
3. **Monitor first few PRs** for remaining issues
4. **Iterate on standards document** based on feedback
5. **Train team members** on the new workflow

---

*This integration should significantly reduce linting errors in AI-generated code and accelerate your development velocity.*