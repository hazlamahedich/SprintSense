# Environment Configuration Guide

## Overview

SprintSense uses environment-specific configuration for local development, staging, and production deployments. This guide explains how to set up and manage these configurations.

## Local Development

### 1. Supabase CLI Setup

```bash
# Install Supabase CLI
npm install -g @supabase/cli

# Initialize local Supabase (if not done)
supabase init

# Start local Supabase stack
supabase start

# Get your local API keys
supabase status
```

### 2. Environment File Setup

```bash
# Copy template and fill values
cp .env.dev.template .env.dev

# Edit .env.dev with your local Supabase keys from `supabase status`
```

### 3. Backend Configuration

```bash
cd backend
cp ../.env.dev .env
poetry install
poetry run uvicorn app.main:app --reload
```

### 4. Frontend Configuration

```bash
cd frontend  
cp ../.env.dev .env.local
npm install
npm run dev
```

## GitHub Environments Setup

### 1. Create Environments

In your GitHub repository:
1. Go to Settings > Environments
2. Create `development`, `staging`, and `production` environments

### 2. Environment Protection Rules

**Staging Environment:**
- Require approvals: 1 reviewer
- Restrict to `main` branch

**Production Environment:**  
- Require approvals: 2 reviewers
- Restrict to `main` branch and tags matching `v*.*.*`
- Wait timer: 5 minutes

### 3. Required Secrets per Environment

#### Development Environment
- `DATABASE_URL`: `postgresql://postgres:postgres@localhost:54322/postgres`
- `SUPABASE_URL`: Your development Supabase project URL
- `SUPABASE_ANON_KEY`: Development anon key
- `SUPABASE_SERVICE_KEY`: Development service key
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications

#### Staging Environment
- `DATABASE_URL`: Staging Supabase database connection string
- `SUPABASE_URL`: Staging Supabase project URL  
- `SUPABASE_ANON_KEY`: Staging anon key
- `SUPABASE_SERVICE_KEY`: Staging service key
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `SENTRY_DSN`: Sentry project DSN (optional)

#### Production Environment
- `DATABASE_URL`: Production Supabase database connection string
- `SUPABASE_URL`: Production Supabase project URL
- `SUPABASE_ANON_KEY`: Production anon key  
- `SUPABASE_SERVICE_KEY`: Production service key
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `SENTRY_DSN`: Sentry project DSN (required)

## Supabase CLI Profiles

### 1. Local Development Profile

```bash
# Already configured when you run `supabase init`
# Uses local Supabase instance at http://127.0.0.1:54321
```

### 2. Cloud Profiles

```bash
# Link to staging project
supabase link --project-ref your-staging-project-ref
supabase db remote commit # Creates a migration baseline

# For production (separate command)
supabase link --project-ref your-production-project-ref
```

### 3. Managing Multiple Projects

```bash
# Create separate directories or use profiles
mkdir -p ~/.config/supabase/profiles/staging
mkdir -p ~/.config/supabase/profiles/production

# Or use environment variables in CI
export SUPABASE_ACCESS_TOKEN=your_access_token
export SUPABASE_PROJECT_REF=your_project_ref
```

## Configuration Validation

### Health Check Endpoints

The application provides health check endpoints to validate configuration:

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Detailed health check (includes database connectivity)
curl http://localhost:8000/api/v1/health/detailed
```

Expected responses:
```json
{
  "status": "OK",
  "service": "SprintSense Backend"
}
```

```json
{
  "status": "OK", 
  "service": "SprintSense Backend",
  "database": "connected",
  "version": "0.1.0"
}
```

### CI/CD Validation

The CI pipeline validates configuration by:

1. **Environment Loading**: Loading `.env` files in GitHub Actions
2. **Health Checks**: Running health check endpoints after deployment
3. **Database Connectivity**: Testing database connections in each environment
4. **Cross-Service Communication**: Validating frontend can reach backend APIs

## Troubleshooting

### Common Issues

1. **Local Supabase Connection Failed**
   ```bash
   # Check if Supabase is running
   supabase status
   
   # Restart if needed
   supabase stop
   supabase start
   ```

2. **Invalid API Keys**
   ```bash
   # Get fresh keys
   supabase status
   
   # Update .env.dev with new keys
   ```

3. **Database Migration Issues**
   ```bash
   # Reset local database
   supabase db reset
   
   # Or create new migration
   supabase db diff --schema public
   ```

4. **CORS Issues**
   - Check `BACKEND_CORS_ORIGINS` includes your frontend URL
   - Ensure no trailing slashes in URLs
   - Verify environment-specific CORS settings

### Environment-Specific Debugging

**Development:**
- Use `LOG_LEVEL=DEBUG` for detailed logging
- Enable FastAPI docs at `/docs` and `/redoc`
- Use local Supabase Studio at http://127.0.0.1:54323

**Staging:**
- Monitor GitHub Actions logs for deployment issues
- Check Supabase logs in cloud dashboard
- Use staging-specific Slack notifications

**Production:**
- Monitor error rates via Sentry
- Check health check endpoints regularly
- Review deployment logs for rollback triggers

## Security Considerations

1. **Never commit secrets to Git**
   - Use `.gitignore` for `.env*` files
   - Store secrets only in GitHub Environments
   - Rotate keys regularly

2. **Environment isolation**
   - Each environment uses separate Supabase projects
   - No shared credentials between environments
   - Staging data should not contain production PII

3. **Access control**
   - Limit GitHub Environment access to team members
   - Use approval gates for production deployments
   - Monitor secret access logs

## Next Steps

Once environment configuration is complete:
1. Test local development setup
2. Configure GitHub secrets for staging/production
3. Run the CI/CD pipeline validation
4. Set up monitoring and alerting