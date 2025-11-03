# SECURITY REMEDIATION - GIT HISTORY CLEANUP

## ⚠️ CRITICAL: This document contains instructions for removing exposed credentials from git history

**Status**: In Progress
**Date**: 2025-11-03
**Priority**: CRITICAL (CVSS 9.1)

---

## 1. IMMEDIATE ACTIONS (COMPLETED)

### ✅ Step 1.1: Generate New Secure Credentials
**Status**: COMPLETED

New credentials generated:
```
JWT_SECRET: AbiepIvrNGL3tkdHeS3kxnutdZ1g84Hzv5rTsnviWKaZ2GdW2eIwwVtqhwuRJCSNGRY56S9yW8MM7elUYDPvow
REFRESH_TOKEN_SECRET: jcMRcQovO1H57ePFJTUsDNzfZ2r9qG_KxaVgsErKIAaIyrdFYUjPuLH6G_79JtxWDi0WDlwOmUcOLKHzv3aDLw
DB_PASSWORD: vtFRkSO_fQiPbO1HUzZu_BPn8doZ03TBG5E1Ux-ejuQ
```

### ✅ Step 1.2: Update Configuration Files
**Status**: COMPLETED

Files updated:
- ✅ `cardinsa-backend/.env` - Updated with new secrets
- ✅ `cardinsa-backend/app/core/database.py` - Removed hardcoded fallback
- ✅ `cardinsa-backend/app/core/settings.py` - Removed hardcoded fallback
- ✅ `cardinsa-backend/alembic.ini` - Removed hardcoded credentials
- ✅ `cardinsa-backend/.env.example` - Updated with security instructions

### ✅ Step 1.3: Verify .gitignore Configuration
**Status**: COMPLETED

.gitignore already properly configured with:
```
.env
.env.*
!.env.example
*.key
*.pem
secrets/
*.secret
```

---

## 2. UPDATE DATABASE PASSWORD (REQUIRED BEFORE TESTING)

### Step 2.1: Update PostgreSQL Password

**IMPORTANT**: The database password has been changed. You must update PostgreSQL before the application can connect.

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Update the password (in psql)
ALTER USER postgres WITH PASSWORD 'vtFRkSO_fQiPbO1HUzZu_BPn8doZ03TBG5E1Ux-ejuQ';

# Verify connection with new password
\q
psql -U postgres -d cardinsa
# Enter password: vtFRkSO_fQiPbO1HUzZu_BPn8doZ03TBG5E1Ux-ejuQ
```

### Step 2.2: Test Application Connection

```bash
cd cardinsa-backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Test database connection
python -c "from app.core.database import engine; engine.connect(); print('✅ Database connection successful')"

# Start application
uvicorn app.main:app --reload
```

---

## 3. REMOVE .env FROM GIT TRACKING (DO THIS NEXT)

### Step 3.1: Stop Tracking .env File

```bash
cd "d:\cardinsa v2"

# Remove .env from git tracking (keeps local file)
git rm --cached cardinsa-backend/.env

# Commit the removal
git add cardinsa-backend/.gitignore
git commit -m "security: Remove .env from version control

- Stop tracking .env file to prevent credential leaks
- .env is now in .gitignore
- See SECURITY_REMEDIATION_STEPS.md for full remediation plan

BREAKING CHANGE: Developers must create their own .env from .env.example"

# Verify .env is no longer tracked
git ls-files | grep "\.env$"
# Should return nothing
```

**⚠️ WARNING**: After this commit, other developers will need to create their own `.env` file from `.env.example`.

---

## 4. CLEAN GIT HISTORY (CRITICAL - DO AFTER STEP 3)

### Why This is Critical

The old credentials are still in git history:
- Old JWT Secret: `Cardinsa_2025@Rasha_N@sri.1982`
- Old DB Password: `Rasha@1973`

These can be extracted from git history even after we stop tracking the file.

### Option A: BFG Repo-Cleaner (RECOMMENDED - Fast & Safe)

**Installation:**
```bash
# Download BFG
# Windows: Download from https://rtyley.github.io/bfg-repo-cleaner/
# Or use Chocolatey:
choco install bfg-repo-cleaner

# Linux/Mac:
brew install bfg
# or
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
```

**Execution:**
```bash
cd "d:\cardinsa v2"

# Create backup first!
cd ..
git clone "d:\cardinsa v2" "d:\cardinsa v2 - backup"

cd "d:\cardinsa v2"

# Remove .env from entire history
bfg --delete-files .env

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to remote (WARNING: Destructive!)
git push origin --force --all
git push origin --force --tags
```

### Option B: git-filter-repo (More Control)

**Installation:**
```bash
pip install git-filter-repo
```

**Execution:**
```bash
cd "d:\cardinsa v2"

# Create backup first!
cd ..
git clone "d:\cardinsa v2" "d:\cardinsa v2 - backup"

cd "d:\cardinsa v2"

# Remove .env from history
git filter-repo --path cardinsa-backend/.env --invert-paths --force

# Force push to remote (WARNING: Destructive!)
git push origin --force --all
git push origin --force --tags
```

### Option C: git filter-branch (Built-in, Slower)

```bash
cd "d:\cardinsa v2"

# Create backup first!
cd ..
git clone "d:\cardinsa v2" "d:\cardinsa v2 - backup"

cd "d:\cardinsa v2"

# Remove .env from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch cardinsa-backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to remote (WARNING: Destructive!)
git push origin --force --all
git push origin --force --tags
```

---

## 5. POST-CLEANUP VERIFICATION

### Step 5.1: Verify Credentials Removed

```bash
cd "d:\cardinsa v2"

# Search for old JWT secret in history
git log -S "Cardinsa_2025@Rasha_N@sri.1982" --all
# Should return no results

# Search for old password in history
git log -S "Rasha@1973" --all
# Should return no results

# Verify .env is not in any commit
git log --all --full-history -- cardinsa-backend/.env
# Should return no results
```

### Step 5.2: Verify Application Still Works

```bash
cd cardinsa-backend

# Test database connection
python -c "from app.core.database import engine; engine.connect(); print('✅ Database connection successful')"

# Test JWT generation
python -c "from app.core.security import create_access_token; token = create_access_token({'sub': 'test'}); print('✅ JWT generation successful')"

# Start application
uvicorn app.main:app --reload --port 8000

# Test health endpoint (in another terminal)
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

## 6. TEAM COMMUNICATION

### Step 6.1: Notify All Developers

Send this message to all developers:

```
🔒 SECURITY UPDATE - ACTION REQUIRED

We have rotated all credentials due to a security audit. Please follow these steps:

1. Pull the latest changes:
   git pull origin main

2. Delete your local .env file:
   rm cardinsa-backend/.env  # or manually delete

3. Create new .env from template:
   cp cardinsa-backend/.env.example cardinsa-backend/.env

4. Request new credentials from [DevOps Lead/Security Team]

5. Update your local database password:
   psql -U postgres
   ALTER USER postgres WITH PASSWORD '[NEW_PASSWORD]';

6. Test your local environment:
   cd cardinsa-backend
   uvicorn app.main:app --reload

If you cloned the repository before [DATE], you need to:
- Delete your local clone
- Clone the repository fresh
- This ensures you don't have old credentials in your local git history

Questions? Contact [Security Lead]
```

### Step 6.2: Update Remote Repository Settings

If hosted on GitHub/GitLab/Bitbucket:

1. **Rotate ALL secrets** in:
   - Repository secrets
   - CI/CD variables
   - Deployment environment variables
   - Any secret scanning alerts

2. **Enable branch protection**:
   - Require pull request reviews
   - Require status checks to pass
   - Restrict force pushes (after history cleanup)

3. **Enable secret scanning**:
   - GitHub: Settings → Security → Secret scanning
   - GitLab: Settings → Repository → Secret detection

---

## 7. ADDITIONAL SECURITY MEASURES

### Step 7.1: Add Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook to prevent committing .env files

if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERROR: Attempting to commit .env file!"
    echo "   .env files should never be committed to git"
    echo "   Use .env.example for template instead"
    exit 1
fi

# Check for potential secrets in staged files
if git diff --cached | grep -E "(password|secret|key|token).*=.*['\"].*['\"]"; then
    echo "⚠️  WARNING: Possible secrets detected in staged files"
    echo "   Please review your changes carefully"
    read -p "   Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Step 7.2: Use Secrets Management (Recommended for Production)

Consider implementing:
- **AWS Secrets Manager** (if using AWS)
- **Azure Key Vault** (if using Azure)
- **HashiCorp Vault** (self-hosted)
- **Doppler** (SaaS)
- **1Password Secrets Automation**

### Step 7.3: Implement Secret Scanning in CI/CD

Add to `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

---

## 8. COMPLIANCE & DOCUMENTATION

### Step 8.1: Security Incident Report

Document this incident:
- **Date Discovered**: 2025-11-03
- **Severity**: CRITICAL (CVSS 9.1)
- **Vulnerability**: Hardcoded credentials in version control
- **Affected Systems**: Development, potentially staging/production
- **Credentials Exposed**:
  - JWT Secret
  - Database password
  - Potentially in git hosting platform (GitHub/GitLab)
- **Remediation**: All credentials rotated, git history cleaned
- **Estimated Exposure Time**: [Calculate from first commit with credentials]
- **Impact Assessment**: [Assess if credentials were accessed]

### Step 8.2: Update Security Documentation

Update project docs to include:
- How to handle secrets securely
- Pre-commit hooks for developers
- .env file management guidelines
- Incident response procedures

---

## 9. VERIFICATION CHECKLIST

Complete this checklist before considering remediation complete:

- [ ] New secrets generated using cryptographically secure method
- [ ] All configuration files updated with new secrets
- [ ] Database password updated in PostgreSQL
- [ ] Application tested and working with new credentials
- [ ] .env removed from git tracking
- [ ] Git history cleaned using BFG/git-filter-repo
- [ ] History verified clean (no old credentials found)
- [ ] Remote repository force-pushed
- [ ] All developers notified
- [ ] All remote secrets rotated (CI/CD, deployment environments)
- [ ] Pre-commit hooks installed
- [ ] Secret scanning enabled
- [ ] Security incident documented
- [ ] Runbook updated with new procedures

---

## 10. ROLLBACK PROCEDURE (If Issues Arise)

If something goes wrong during git history cleanup:

```bash
# Restore from backup
cd "d:\cardinsa v2 - backup"
git fetch origin
git reset --hard origin/main

# Or restore the backup
cd "d:\"
rm -rf "cardinsa v2"
cp -r "cardinsa v2 - backup" "cardinsa v2"
cd "cardinsa v2"
```

**⚠️ IMPORTANT**: Keep the backup until you've verified everything works for at least 7 days.

---

## NEXT STEPS

After completing this remediation:

1. Continue with **Phase 1, Day 3**: Fix SQL injection vulnerability
2. Continue with **Phase 1, Day 4**: Fix async permission check bypass
3. Continue with **Phase 1, Day 5**: Fix CORS misconfiguration

See main remediation plan in conversation history.

---

## SUPPORT & QUESTIONS

If you encounter issues:
1. Check the backup before making destructive changes
2. Test in a separate clone first
3. Consult with security team before force-pushing
4. Document all steps taken

**Remember**: Force-pushing rewrites history and can disrupt other developers. Coordinate with the team!
