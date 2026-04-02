# CI/CD Pipeline Setup Guide

Your project now has a complete CI/CD pipeline set up with GitHub Actions. Here's what's configured:

## Workflows

### 1. **Test & Validate** (`test.yml`)
Runs on:
- Pull requests to `main` or `develop`
- Pushes to `develop`

Tasks:
- ✅ Runs pytest on all tests
- ✅ Checks code quality with pylint
- ✅ Validates code formatting with black

### 2. **Deploy to Databricks** (`deploy.yml`)
Runs on:
- Pushes to `main` branch

Tasks:
- ✅ Deploys the bundle to production Databricks workspace
- ✅ Uses Databricks CLI for deployment

## Required GitHub Secrets

Add the following secrets to your GitHub repository settings (Settings → Secrets and variables → Actions):

1. **DATABRICKS_HOST** - Your Databricks workspace URL
   - Example: `https://adb-xxx-prod.azuredatabricks.net`

2. **DATABRICKS_TOKEN** - Your Databricks personal access token
   - Generate from Databricks workspace: Settings → Developer → Personal access tokens

3. **NOTIFICATION_EMAILS** - Comma-separated emails for failure notifications
   - Example: `user1@example.com,user2@example.com`

## Setup Instructions

1. **Add secrets to GitHub**
   ```
   Repository → Settings → Secrets and variables → Actions → New repository secret
   ```

2. **Ensure tests are working locally**
   ```bash
   pip install -r requirements.txt
   pytest tests/ -v
   ```

3. **Push to develop or create a PR to main**
   - CI pipeline will automatically run tests
   - Once tests pass, merge to main to trigger deployment

## Git Workflow

```
Feature branch → develop → PR → main → Deploy to Databricks
     ↓
   Test CI
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Format code
black src/ tests/

# Check code quality
pylint src/
```

## Monitoring

- Check workflow status: Go to Actions tab in GitHub
- View logs for each workflow run
- Deployment logs show Databricks bundle deployment status
