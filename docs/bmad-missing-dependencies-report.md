# BMad Method Missing Dependencies Report

## Executive Summary

- **Total referenced files**: 126
- **Total actual files**: 105
- **Missing files**: 53

## Missing Files by Category

### Data Files (1 missing)

| File | Referenced By | Likely Purpose |
|------|---------------|----------------|
| `data/technical-preferences.yaml` | templates:architecture-tmpl.yaml, templates:prd-tmpl.yaml | Reference data or knowledge base |

### Other Files (49 missing)

| File | Referenced By | Likely Purpose |
|------|---------------|----------------|
| `CONTRIBUTING.md` | data:bmad-kb.md, data:bmad-kb.md | Support document |
| `another.md` | tasks:index-docs.md, tasks:index-docs.md | Support document |
| `ci.yaml` | templates:fullstack-architecture-tmpl.yaml | Support document |
| `.ai/debug-log.md` | core-config.yaml | Support document |
| `tech-stack.md` | tasks:shard-doc.md, tasks:create-next-story.md | Support document |
| `requirements.md` | data:bmad-kb.md | Support document |
| `backend-architecture.md` | tasks:create-next-story.md | Support document |
| `brainstorming-session-results.md` | templates:brainstorming-output-tmpl.yaml, tasks:facilitate-brainstorming-session.md | Support document |
| `troubleshooting.md` | tasks:document-project.md | Support document |
| `docs/architecture/tech-stack.md` | core-config.yaml:devLoadAlwaysFiles | Support document |
| `section-name-1.md` | tasks:shard-doc.md, tasks:shard-doc.md | Support document |
| `section-name-2.md` | tasks:shard-doc.md, tasks:shard-doc.md | Support document |
| `expansion-packs.md` | data:bmad-kb.md | Support document |
| `rest-api-spec.md` | tasks:create-next-story.md | Support document |
| `success-metrics.md` | data:bmad-kb.md | Support document |
| `unified-project-structure.md` | tasks:create-next-story.md, tasks:create-next-story.md, tasks:review-story.md | Support document |
| `goals-and-background-context.md` | data:bmad-kb.md | Support document |
| `project-architecture.md` | tasks:document-project.md | Support document |
| `file.md` | tasks:index-docs.md, tasks:index-docs.md | Support document |
| `epic-retrospective.md` | workflows:greenfield-ui.yaml, workflows:brownfield-fullstack.yaml, workflows:brownfield-ui.yaml (+3 more) | Support document |
| `typescript-rules.md` | tasks:apply-qa-fixes.md | Support document |
| `brownfield-prd.md` | templates:brownfield-architecture-tmpl.yaml, checklists:po-master-checklist.md, checklists:po-master-checklist.md | Support document |
| `ui-architecture.md` | templates:front-end-architecture-tmpl.yaml | Support document |
| `story.md` | workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml (+25 more) | Support document |
| `docs/architecture/source-tree.md` | core-config.yaml:devLoadAlwaysFiles | Support document |
| `testing-strategy.md` | tasks:create-next-story.md, tasks:create-next-story.md, tasks:review-story.md | Support document |
| `user-interface-design-goals.md` | data:bmad-kb.md | Support document |
| `external-apis.md` | tasks:create-next-story.md | Support document |
| `README.md` | templates:fullstack-architecture-tmpl.yaml, tasks:index-docs.md | Support document |
| `front-end-architecture.md` | workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml (+2 more) | Support document |
| `database-schema.md` | tasks:create-next-story.md | Support document |
| `components.md` | tasks:create-next-story.md | Support document |
| `data-models.md` | tasks:create-next-story.md, tasks:create-next-story.md | Support document |
| `openapi.yaml` | tasks:document-project.md | Support document |
| `epic-n.md` | data:bmad-kb.md | Support document |
| `core-workflows.md` | tasks:create-next-story.md | Support document |
| `document.md` | tasks:index-docs.md, tasks:index-docs.md, tasks:index-docs.md | Support document |
| `section-name-3.md` | tasks:shard-doc.md | Support document |
| `fe-architecture.md` | checklists:architect-checklist.md | Support document |
| `GUIDING-PRINCIPLES.md` | data:bmad-kb.md | Support document |
| `market-research.md` | templates:market-research-tmpl.yaml | Support document |
| `competitor-analysis.md` | templates:competitor-analysis-tmpl.yaml | Support document |
| `filename.md` | checklists:story-draft-checklist.md | Support document |
| `deploy.yaml` | templates:fullstack-architecture-tmpl.yaml | Support document |
| `fullstack-architecture.md` | templates:fullstack-architecture-tmpl.yaml, workflows:greenfield-fullstack.yaml, workflows:greenfield-fullstack.yaml (+3 more) | Support document |
| `frontend-architecture.md` | tasks:create-next-story.md, checklists:architect-checklist.md, checklists:architect-checklist.md (+3 more) | Support document |
| `technical-preferences.yaml` | templates:architecture-tmpl.yaml, templates:prd-tmpl.yaml | Support document |
| `brownfield-architecture.md` | workflows:brownfield-fullstack.yaml, tasks:create-brownfield-story.md, tasks:create-brownfield-story.md (+4 more) | Support document |
| `project-brief.md` | workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml, workflows:greenfield-ui.yaml (+12 more) | Support document |

### Template Files (3 missing)

| File | Referenced By | Likely Purpose |
|------|---------------|----------------|
| `brownfield-architecture-tmpl.md` | data:bmad-kb.md | Architecture document template |
| `brownfield-prd-tmpl.md` | data:bmad-kb.md | Product Requirements Document template |
| `story-tmpl.md` | tasks:validate-next-story.md | User story template |

## Recommendations

1. **Create missing files**: Start with the most referenced files
2. **Update references**: Some files may exist with different names/paths
3. **Clean up**: Remove references to files that are no longer needed
