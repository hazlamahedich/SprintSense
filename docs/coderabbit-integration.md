# Code Rabbit Integration Guide

This document explains how Code Rabbit is integrated into SprintSense's development workflow for automated code reviews.

## Overview

Code Rabbit provides AI-powered code reviews that run automatically on:
- **Pull Requests**: When opened, updated, or marked ready for review
- **Direct Commits**: When pushed to main or develop branches
- **Manual Reviews**: Via Warp terminal integration

## Table of Contents

1. [Architecture](#architecture)
2. [Warp Terminal Integration](#warp-terminal-integration)
3. [GitHub Actions Integration](#github-actions-integration)
4. [Configuration](#configuration)
5. [Review Process](#review-process)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Code Rabbit Integration                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐  │
│  │                 │    │                     │    │                     │  │
│  │  Warp Terminal  │    │   GitHub Actions    │    │   Repository Rules  │  │
│  │                 │    │                     │    │                     │  │
│  │  • MCP Client   │    │  • PR Reviews       │    │  • .coderabbit.yml  │  │
│  │  • Manual       │────┤  • Push Reviews     │────┤  • Exclusions       │  │
│  │    Reviews      │    │  • Status Checks    │    │  • Custom Rules     │  │
│  │                 │    │                     │    │                     │  │
│  └─────────────────┘    └─────────────────────┘    └─────────────────────┘  │
│           │                        │                         │              │
│           │                        │                         │              │
│           └────────────────────────┼─────────────────────────┘              │
│                                    │                                        │
│              ┌─────────────────────▼─────────────────────┐                  │
│              │                                           │                  │
│              │            Code Rabbit API               │                  │
│              │                                           │                  │
│              │  • AI Code Analysis                      │                  │
│              │  • Security Review                       │                  │
│              │  • Performance Analysis                  │                  │
│              │  • Best Practice Enforcement             │                  │
│              │                                           │                  │
│              └─────────────────────────────────────────────┘                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Warp Terminal Integration

### Setup

Code Rabbit MCP is configured in Warp to provide terminal-based code reviews:

**Configuration Location**: `~/Library/Application Support/dev.warp.Warp-Stable/mcp/config.json`

```json
{
    "coderabbit": {
        "command": "npx",
        "args": ["-y", "coderabbitai-mcp"],
        "env": {
            "GITHUB_PAT": "your_github_personal_access_token"
        }
    }
}
```

### Usage

Once configured, you can:

1. **Manual Code Review**: Select code in your terminal/editor and use AI commands
2. **File Analysis**: Review entire files before committing
3. **Diff Analysis**: Analyze changes before pushing

### Commands Available

- Code quality analysis
- Security vulnerability detection
- Performance optimization suggestions
- Best practice recommendations

---

## GitHub Actions Integration

### Workflow Configuration

Code Rabbit runs as a GitHub Action in `.github/workflows/coderabbit-review.yml`.

### Triggers

- **Pull Requests**: `opened`, `synchronize`, `reopened`, `ready_for_review`
- **Pushes**: to `main` or `develop` branches
- **File Changes**: Only when relevant code files are modified

### Review Process

1. **Change Detection**: Identifies modified files
2. **Context Analysis**: Understands SprintSense architecture
3. **Code Review**: Analyzes code quality, security, performance
4. **Comment Generation**: Creates detailed inline and summary comments
5. **Status Check**: Reports pass/fail status for CI/CD gates

### Integration with Existing CI/CD

Code Rabbit runs **independently** alongside the existing CI pipeline:

```yaml
# Both workflows trigger on the same events
┌─────────────────┐     ┌─────────────────┐
│   CI Workflow   │     │  CodeRabbit     │
│                 │     │  Workflow       │
│ • Backend tests │     │ • Code analysis │
│ • Frontend tests│◄────┤ • Security scan │
│ • Build checks  │     │ • Review comments│
│ • Deploy        │     │ • Status check  │
└─────────────────┘     └─────────────────┘
```

### Permissions Required

- `contents: read` - Access repository code
- `pull-requests: write` - Post review comments
- `issues: write` - Create issue comments
- `repository-projects: read` - Access project context

---

## Configuration

### Repository Configuration: `.coderabbit.yml`

Located at the repository root, this file configures Code Rabbit's behavior:

```yaml
# Base configuration
base_branch: main
comment_mode: review
enable_auto_review: true

# Custom rules aligned with SprintSense standards
rules:
  - file: docs/architecture.md          # Project architecture guide
  - file: claude_suggestions.md         # AI-generated suggestions
  
  - name: "Python Code Quality"
    pattern: "**/*.py"
    checks:
      - "Follow PEP 8 style guidelines"
      - "Use type hints"
      - "Use Poetry for dependencies"
      
  - name: "TypeScript/JavaScript Quality"
    pattern: "**/*.{ts,tsx,js,jsx}"
    checks:
      - "Use TypeScript strict mode"
      - "Follow ESLint rules"

# Exclusions
exclude:
  - "**/node_modules/**"
  - "**/.venv/**"
  - "**/__pycache__/**"
  - ".bmad-core/**"

# Review intensity
review_settings:
  high_priority_paths:
    - "backend/app/api/**"
    - "frontend/src/api/**"
    - ".github/workflows/**"
```

### Environment Variables

```bash
# Required for GitHub Actions
CODERABBIT_API_TOKEN=your_api_token

# Required for Warp MCP integration  
GITHUB_PAT=your_github_token
```

### Secrets Configuration

Set these in GitHub repository secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add **CODERABBIT_API_TOKEN**
3. Ensure **GITHUB_TOKEN** has appropriate permissions

---

## Review Process

### For Pull Requests

1. **Automatic Trigger**: Code Rabbit starts when PR is opened/updated
2. **File Analysis**: Reviews only changed files
3. **Contextual Review**: Understands PR context and purpose
4. **Inline Comments**: Provides specific line-by-line feedback
5. **Summary Comment**: Posts overall assessment
6. **Status Check**: Reports pass/fail for merge requirements

### For Direct Commits

1. **Push Detection**: Triggered on commits to main/develop
2. **Full Analysis**: Reviews all changed files
3. **Issue Creation**: Creates issues for critical findings
4. **Team Notification**: Alerts team to significant issues

### Review Focus Areas

- **Code Quality**: Maintainability, readability, best practices
- **Security**: Vulnerability detection, secure coding practices
- **Performance**: Optimization opportunities, bottlenecks
- **Architecture**: Consistency with SprintSense design patterns
- **Testing**: Test coverage, test quality
- **Documentation**: Code comments, API documentation

---

## Troubleshooting

### Common Issues

**1. Code Rabbit Not Triggering**
- Check file patterns in workflow triggers
- Verify GitHub Actions are enabled
- Confirm secrets are properly set

**2. Permission Errors**
```bash
Error: Resource not accessible by integration
```
- Verify `GITHUB_TOKEN` permissions
- Check repository permissions
- Ensure Code Rabbit has access to repository

**3. Review Comments Not Appearing**
- Check PR is not in draft mode (unless enabled)
- Verify Code Rabbit API token is valid
- Check workflow run logs for errors

**4. Warp MCP Not Working**
- Restart Warp after configuration changes
- Verify MCP configuration syntax
- Check GitHub PAT permissions

### Debug Steps

1. **Check Workflow Logs**:
   ```bash
   # Go to Actions tab in GitHub
   # Click on failed workflow run
   # Expand Code Rabbit step logs
   ```

2. **Validate Configuration**:
   ```bash
   # Test .coderabbit.yml syntax
   npx yaml-lint .coderabbit.yml
   ```

3. **Test API Token**:
   ```bash
   # Test Code Rabbit API access
   curl -H "Authorization: Bearer $CODERABBIT_API_TOKEN" \
        https://api.coderabbit.ai/v1/user
   ```

---

## Best Practices

### For Developers

1. **Address Reviews Promptly**
   - Review Code Rabbit feedback before requesting human review
   - Address critical security issues immediately
   - Consider performance suggestions seriously

2. **Use Descriptive Commit Messages**
   - Help Code Rabbit understand change context
   - Include ticket numbers and brief descriptions

3. **Test Changes Locally**
   - Use Warp integration for pre-commit reviews
   - Address obvious issues before pushing

### For Code Quality

1. **Follow Established Patterns**
   - Align with existing SprintSense architecture
   - Reference `docs/architecture.md` for guidance
   - Consider suggestions in `claude_suggestions.md`

2. **Security First**
   - Address all security-related feedback
   - Use secure coding practices
   - Validate input and sanitize output

3. **Performance Awareness**
   - Consider performance implications of changes
   - Optimize database queries
   - Mind frontend bundle size

### For Team Collaboration

1. **Review Integration Results**
   - Discuss recurring issues in team meetings
   - Update `.coderabbit.yml` based on team feedback
   - Share knowledge about common Code Rabbit suggestions

2. **Continuous Improvement**
   - Monitor Code Rabbit effectiveness
   - Adjust configuration based on false positives/negatives
   - Keep documentation updated

---

## Compliance with Project Rules

This integration adheres to established SprintSense project rules:

- **BC73BsemmfLkKZmGzdCOY0**: References coding standards and `claude_suggestions.md`
- **ktlFUZTBDGfzx5bGDaUqew**: Integrates with QA approval process
- **sqHKIFU46esa5UYGyAAL9K**: Enforces Poetry usage for Python dependencies

---

## Support and Feedback

For issues or suggestions regarding Code Rabbit integration:

1. **Check Logs**: Review GitHub Actions logs first
2. **Update Documentation**: Keep this guide current with changes
3. **Team Discussion**: Use GitHub Discussions for feedback
4. **Configuration Updates**: Propose changes via pull requests

---

**Last Updated**: [Current Date]
**Version**: 1.0
**Changelog**:
- 1.0: Initial Code Rabbit integration with Warp MCP and GitHub Actions
