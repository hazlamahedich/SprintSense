# SprintSense CI/CD Rollback Procedures

## Quick Rollback Commands

### 1. Immediate Rollback via Git Revert
```bash
# Find the problematic commit
git log --oneline -5

# Revert the problematic commit (creates new commit)
git revert <commit-sha> --no-edit

# Push to trigger automatic rollback deployment
git push origin main
```

### 2. Docker Container Rollback
```bash
# If using Docker Compose
cd ops
docker-compose pull  # Get previous images
docker-compose up -d --force-recreate

# If using Kubernetes
kubectl rollout undo deployment/sprintsense-backend
kubectl rollout undo deployment/sprintsense-frontend
kubectl rollout status deployment/sprintsense-backend
```

### 3. Database Rollback (Use with Caution!)
```bash
cd backend

# Check migration history
poetry run alembic history

# Rollback to specific version (DANGEROUS - data loss possible)
poetry run alembic downgrade <revision_id>
```

## Post-Deployment Validation Checklist

### ✅ Functional Testing
- [ ] **Authentication**: Login/logout works
- [ ] **Work Items**: Can create, view, edit work items
- [ ] **Manual Prioritization**: Can move items up/down/top/bottom
- [ ] **Soft Delete**: Can archive items (Story 2.5)
- [ ] **Priority Controls**: All buttons work with keyboard nav (Story 2.6)

### ✅ Performance Testing
- [ ] **API Response Times**: < 1 second for all endpoints
- [ ] **Health Checks**: `/api/v1/health` returns 200
- [ ] **Database**: All queries complete within acceptable time
- [ ] **Frontend**: Page loads < 3 seconds

### ✅ Accessibility Testing (Story 2.6 Requirement)
- [ ] **Screen Reader**: Priority buttons have correct ARIA labels
- [ ] **Keyboard Navigation**: Tab order works correctly
- [ ] **Focus Management**: Visible focus indicators
- [ ] **Color Contrast**: Meets WCAG 2.1 AA standards

### ✅ Error Handling
- [ ] **Network Errors**: Graceful degradation
- [ ] **Conflict Resolution**: 409 errors show user-friendly messages
- [ ] **Validation**: Form errors display correctly
- [ ] **Loading States**: All operations show progress indicators

## Emergency Contacts

- **On-Call Engineer**: [Configure your team's contact info]
- **DevOps Team**: [Configure your team's contact info]  
- **QA Team**: Quinn (QA Architect who approved Stories 2.5 & 2.6)

## Monitoring URLs

- **GitHub Actions**: <https://github.com/hazlamahedich/SprintSense/actions>
- **Health Dashboard**: <https://dev.api.sprintsense.io/docs#/Health>
- **Deployment Status**: [Configure your deployment dashboard URL]

## Recovery Time Objectives

- **Critical Issues**: < 15 minutes (immediate git revert + push)
- **Major Issues**: < 30 minutes (container rollback)
- **Minor Issues**: < 1 hour (hotfix deployment)

---

**Last Updated**: 2025-09-19  
**Pipeline Version**: commit `c6baf28`  
**QA Approved Features**: Stories 2.5 (Soft Delete), 2.6 (Manual Prioritization)
