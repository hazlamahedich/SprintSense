# BMAD Document Location Rules

## Overview
This document defines the standardized locations and naming conventions for BMAD-related documents in the project. All paths are configured in `bmad-core/core-config.yaml` and are relative to the project root.

## Story Documents

### Location
- Base Path: `docs/stories`
- Configuration: `devStoryLocation` in `bmad-core/core-config.yaml`

### Naming Convention
- Format: `{epic_num}.{story_num}.{story_title_short}.md`
- Example: `1.23.user-authentication.md`

## QA Gate Documents

### Location
- Base Path: `docs/qa/gates`
- Configuration: `qa.qaLocation` in `bmad-core/core-config.yaml`

### Naming Convention
- Format: `{epic}.{story}-{slug}.yml`
- Example: `1.23-authentication-flow.yml`

### Story Reference Requirement
- Every QA gate must be referenced in the story's QA Results section
- Use the standardized format:
```markdown
Gate: {STATUS} → qa.qaLocation/gates/{epic}.{story}-{slug}.yml
```

## QA Assessment Documents

### Risk Profiles
- Path: `docs/qa/assessments`
- Format: `{epic}.{story}-risk-{YYYYMMDD}.md`
- Example: `1.23-risk-20231201.md`

### NFR Assessments
- Path: `docs/qa/assessments`
- Format: `{epic}.{story}-nfr-{YYYYMMDD}.md`
- Example: `1.23-nfr-20231201.md`

## Naming Standards

### Slug Rules
1. Convert all text to lowercase
2. Replace spaces with hyphens
3. Remove all punctuation except hyphens
4. Use only alphanumeric characters and hyphens

Examples:
```
Good: 1.23-user-auth-flow.yml
Bad: 1.23_UserAuth_Flow.yml
```

### Date Format
1. Use YYYYMMDD format consistently
2. No separators in date strings

Examples:
```
Good: 1.23-risk-20231201.md
Bad: 1.23-risk-2023-12-01.md
```

## Directory Structure
```
docs/
├── stories/
│   └── 1.23.user-authentication.md
├── qa/
│   ├── gates/
│   │   └── 1.23-auth-flow.yml
│   └── assessments/
│       ├── 1.23-risk-20231201.md
│       └── 1.23-nfr-20231201.md
```

## Validation Rules
1. All paths must be relative to project root
2. Configuration values must exist in `core-config.yaml`
3. All document references must use standardized format
4. Date formats must be consistent
5. File and directory names must follow slug rules
6. Stories must include QA gate references when applicable

## Change Log
| Date | Description | Author |
|------|-------------|--------|
| 2025-09-24 | Initial documentation of BMAD document location rules | AI Assistant |
