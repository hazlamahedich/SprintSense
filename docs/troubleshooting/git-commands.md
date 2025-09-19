# Git Command Troubleshooting Guide

## Issue: Git Command Hanging

### Problem Description
The git command `git log --oneline -10 --grep="deploy" --name-only` was getting stuck and not returning results.

### Root Cause
The combination of `--oneline` and `--name-only` flags with `--grep` can cause git to hang or behave unexpectedly. This is a known compatibility issue where the output formatting conflicts with the file listing functionality.

### Solution

#### ❌ Problematic Command
```bash
git log --oneline -10 --grep="deploy" --name-only
```

#### ✅ Fixed Commands

**Option 1: Use --pretty=format instead (Recommended)**
```bash
git --no-pager log --grep="deploy" -10 --pretty=format:"%h %s" --name-only
```

**Option 2: Use --stat instead of --name-only**
```bash
git --no-pager log --oneline -10 --grep="deploy" --stat
```

**Option 3: Separate operations (Safest)**
```bash
# First get commits
git --no-pager log --oneline -10 --grep="deploy"

# Then get files for specific commits
git --no-pager show --name-only <commit-hash>
```

### Prevention Best Practices

1. **Always use --no-pager**: Prevents git from launching interactive pagers that could cause hanging
2. **Test flag combinations**: When building complex git commands, test each flag combination separately
3. **Avoid mixing formatting flags**: Don't combine `--oneline` with `--name-only`
4. **Use timeouts in scripts**: Consider adding timeout mechanisms in automated scripts

### Available Tools

We've created a deployment utilities script that provides safe alternatives:

```bash
# Show recent deployment commits with files (fixed version)
./scripts/deploy-utils.sh commits-and-files 10

# Safe alternative method
./scripts/deploy-utils.sh commits-safe 10

# Deployment statistics
./scripts/deploy-utils.sh stats

# Check repository state
./scripts/deploy-utils.sh check
```

Or use the Makefile targets:

```bash
make deploy-status      # Show deployment statistics
make deploy-commits     # Show recent deployment commits with files
make deploy-check       # Check git repository state
```

### Git Command Reference

#### Safe Git Log Combinations

```bash
# Get commit info only
git --no-pager log --grep="deploy" -10 --oneline

# Get files changed in commits
git --no-pager log --grep="deploy" -10 --name-only --pretty=format:"%h %s"

# Get detailed stats
git --no-pager log --grep="deploy" -10 --stat

# Get commit hashes only
git --no-pager log --grep="deploy" -10 --pretty=format:"%H"
```

#### Debugging Hung Git Commands

If a git command gets stuck:

1. **Kill the process**:
   ```bash
   # Find the process
   ps aux | grep git

   # Kill it
   kill <process-id>
   ```

2. **Check for interactive prompts**: The command might be waiting for user input

3. **Add --no-pager**: Ensure git doesn't try to use a pager

4. **Test simpler versions**: Remove flags one by one to isolate the issue

### Workflow Integration

The fixed commands are now integrated into:
- `scripts/deploy-utils.sh` - Comprehensive deployment utilities
- `Makefile` - Quick access via make targets
- This troubleshooting guide - For future reference

### Related Issues

This issue commonly occurs with:
- Git commands in CI/CD pipelines
- Automated deployment scripts
- Git hooks that process commit information
- Scripts that analyze repository history

Always test git commands interactively before adding them to automation scripts.
