# Publish Documentation Site

Description: Deploys built documentation site to hosting providers (GitHub Pages, Vercel, or Netlify).

Arguments:
- target: Required. One of: "github-pages", "vercel", "netlify"
- source: (optional) Path to built site. Default: "site/"
- branch: (optional) For GitHub Pages deployment branch. Default: "gh-pages"
- domain: (optional) Custom domain to configure

---

You are executing a three-phase documentation deployment pipeline. Read CLAUDE.md first for project context.

**Prerequisite:** Run `/doc-build` first to generate the deployable site.

---

## THREE-PHASE PIPELINE

### PHASE 1: VALIDATOR
*Persona: DevOps Engineer validating build*
- Verify built site exists at source path
- Detect platform type from configuration files
- Validate site structure matches platform requirements
- Check for required deployment prerequisites

### PHASE 2: CONFIGURATOR
*Persona: Platform Deployment Specialist*
- Generate deployment configuration files
- Set up CI/CD workflow if needed
- Configure custom domain if provided
- Prepare deployment commands

### PHASE 3: DEPLOYER
*Persona: Release Engineer executing deployment*
- Execute deployment steps
- Verify deployment succeeded
- Report live URL and next steps

---

## PHASE 1: BUILD VALIDATION

### Step 1.1: Verify Source Exists

Check that `$source` directory exists:
```bash
ls -la $source
```

If not found, output error:
```
Error: No built site found at $source
       Run /doc-build first to generate the site.
```

### Step 1.2: Detect Platform Type

Check for platform indicator files:

| Platform | Indicator Files |
|----------|-----------------|
| Jekyll | `_config.yml`, `Gemfile` |
| Docusaurus | `docusaurus.config.js`, `package.json` |
| MkDocs | `mkdocs.yml` |

### Step 1.3: Validate Site Structure

**Jekyll:**
- [ ] `_config.yml` exists and is valid YAML
- [ ] `index.md` or `index.html` exists
- [ ] At least one content file with frontmatter

**Docusaurus:**
- [ ] `docusaurus.config.js` exists
- [ ] `docs/` directory with content
- [ ] `package.json` with required dependencies

**MkDocs:**
- [ ] `mkdocs.yml` exists and is valid YAML
- [ ] `docs/index.md` exists
- [ ] Nav structure references existing files

### Step 1.4: Check Prerequisites

**GitHub Pages:**
- [ ] Git repository initialized
- [ ] Remote origin configured
- [ ] User has push access (cannot verify, will fail at deploy)

**Vercel:**
- [ ] Check if `vercel` CLI available: `which vercel`
- [ ] If not, provide installation instructions

**Netlify:**
- [ ] Check if `netlify` CLI available: `which netlify`
- [ ] If not, provide installation instructions

---

## PHASE 2: DEPLOYMENT CONFIGURATION

### Target: GitHub Pages

#### Step 2.1: Determine Deployment Method

**Option A: GitHub Actions (Recommended)**
- Works with any static site generator
- Builds on push, no local build required
- Supports custom domains

**Option B: Direct gh-pages Branch Push**
- Requires local build
- Simpler for Jekyll (GitHub builds natively)
- Manual deployment

Default to **Option A** (GitHub Actions) unless Jekyll detected AND no custom build needed.

#### Step 2.2: Generate GitHub Actions Workflow

Create `.github/workflows/docs.yml`:

Use template from `templates/github-actions/docs.yml.template` with substitutions:

| Placeholder | Source |
|-------------|--------|
| `{{PLATFORM}}` | Detected platform (jekyll, docusaurus, mkdocs) |
| `{{SOURCE_PATH}}` | $source argument |
| `{{NODE_VERSION}}` | "20" for Docusaurus |
| `{{PYTHON_VERSION}}` | "3.x" for MkDocs |
| `{{RUBY_VERSION}}` | "3.2" for Jekyll |

#### Step 2.3: Configure Custom Domain (if provided)

Create `$source/CNAME` file:
```
{{DOMAIN}}
```

Add to `_config.yml` (Jekyll):
```yaml
url: "https://{{DOMAIN}}"
baseurl: ""
```

Or `docusaurus.config.js`:
```javascript
url: 'https://{{DOMAIN}}',
baseUrl: '/',
```

Or `mkdocs.yml`:
```yaml
site_url: https://{{DOMAIN}}
```

#### Step 2.4: Output Deployment Instructions

```
GitHub Pages Deployment Configured

Files created:
- .github/workflows/docs.yml

Next steps:
1. Commit and push changes:
   git add .github/workflows/docs.yml
   git commit -m "Add documentation deployment workflow"
   git push origin main

2. Enable GitHub Pages in repository settings:
   - Go to Settings > Pages
   - Source: GitHub Actions

3. The workflow will run automatically on push to main

Expected URL: https://{{USERNAME}}.github.io/{{REPO_NAME}}/
```

---

### Target: Vercel

#### Step 2.1: Check Vercel CLI

```bash
vercel --version
```

If not installed:
```
Vercel CLI not found. Install with:
  npm install -g vercel

Then run /doc-publish again.
```

#### Step 2.2: Generate vercel.json

Create `$source/vercel.json`:

**For Jekyll (pre-built):**
```json
{
  "version": 2,
  "name": "{{PROJECT_NAME}}-docs",
  "builds": [
    {
      "src": "_site/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/_site/$1"
    }
  ]
}
```

**For Docusaurus:**
```json
{
  "version": 2,
  "name": "{{PROJECT_NAME}}-docs",
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus-2"
}
```

**For MkDocs:**
```json
{
  "version": 2,
  "name": "{{PROJECT_NAME}}-docs",
  "buildCommand": "mkdocs build",
  "outputDirectory": "site",
  "installCommand": "pip install mkdocs-material"
}
```

#### Step 2.3: Execute Deployment

```bash
cd $source
vercel --prod
```

If custom domain provided:
```bash
vercel --prod --name={{DOMAIN}}
```

#### Step 2.4: Configure Custom Domain (if provided)

```bash
vercel domains add {{DOMAIN}}
```

---

### Target: Netlify

#### Step 2.1: Check Netlify CLI

```bash
netlify --version
```

If not installed:
```
Netlify CLI not found. Install with:
  npm install -g netlify-cli

Then run /doc-publish again.
```

#### Step 2.2: Generate netlify.toml

Create `$source/netlify.toml`:

**For Jekyll:**
```toml
[build]
  publish = "_site"
  command = "jekyll build"

[build.environment]
  RUBY_VERSION = "3.2"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**For Docusaurus:**
```toml
[build]
  publish = "build"
  command = "npm run build"

[build.environment]
  NODE_VERSION = "20"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**For MkDocs:**
```toml
[build]
  publish = "site"
  command = "mkdocs build"

[build.environment]
  PYTHON_VERSION = "3.11"

[[plugins]]
  package = "@netlify/plugin-local-install-core"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### Step 2.3: Execute Deployment

```bash
cd $source
netlify deploy --prod
```

If first time, this will prompt for:
- Team selection
- Site name
- Build settings confirmation

#### Step 2.4: Configure Custom Domain (if provided)

After deployment:
```bash
netlify domains:add {{DOMAIN}}
```

---

## PHASE 3: VERIFICATION

### Step 3.1: Verify Deployment Success

**GitHub Pages:**
- Check workflow run status:
```bash
gh run list --workflow=docs.yml --limit=1
```
- Expected: Completed successfully

**Vercel:**
- Check deployment output for URL
- Verify site is accessible

**Netlify:**
- Check deployment output for URL
- Verify site is accessible

### Step 3.2: Test Live Site

Attempt to fetch the deployed URL:
```bash
curl -I {{LIVE_URL}}
```

Expected: HTTP 200 response

### Step 3.3: Generate Deployment Report

```
╔════════════════════════════════════════════════════════════════════╗
║  Documentation Deployed Successfully                                ║
╠════════════════════════════════════════════════════════════════════╣
║  Platform: [jekyll|docusaurus|mkdocs]                               ║
║  Target: [github-pages|vercel|netlify]                              ║
║  Source: $source                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║  Live URL: {{LIVE_URL}}                                             ║
║  Custom Domain: {{DOMAIN}} (if configured)                          ║
╠════════════════════════════════════════════════════════════════════╣
║  Deployment Details:                                                ║
║  - [Platform-specific details]                                      ║
╠════════════════════════════════════════════════════════════════════╣
║  Next Steps:                                                        ║
║  - Verify all pages render correctly                                ║
║  - Test navigation and search                                       ║
║  - Configure DNS for custom domain (if applicable)                  ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## CUSTOM DOMAIN DNS SETUP

If custom domain is configured, provide DNS instructions:

### For Apex Domain (example.com)

```
Add these DNS records at your domain registrar:

Type    Name    Value
----    ----    -----
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
```

### For Subdomain (docs.example.com)

```
Add this DNS record at your domain registrar:

Type    Name    Value
----    ----    -----
CNAME   docs    [your-site-url]
```

**Vercel:** CNAME to `cname.vercel-dns.com`
**Netlify:** CNAME to `[site-name].netlify.app`
**GitHub Pages:** CNAME to `[username].github.io`

---

## ERROR HANDLING

| Error | Resolution |
|-------|------------|
| No site found at source | Run `/doc-build` first |
| Unknown platform type | Ensure build was successful |
| CLI not installed | Provide installation command |
| Authentication failed | Guide user to login |
| Deployment failed | Show error details, suggest fixes |
| DNS not configured | Provide DNS setup instructions |

---

## ROLLBACK INSTRUCTIONS

If deployment has issues:

**GitHub Pages:**
```bash
# Revert to previous workflow
git revert HEAD
git push origin main
```

**Vercel:**
```bash
# List deployments
vercel ls

# Promote previous deployment
vercel promote [deployment-url]
```

**Netlify:**
```bash
# List deploys
netlify deploys

# Rollback to previous
netlify deploy --prod --alias previous
```

---

## CRITICAL RULES

1. **Always validate build first** - Don't deploy invalid sites
2. **Preserve existing configurations** - Merge, don't overwrite
3. **Provide clear feedback** - Report URL and status
4. **Handle failures gracefully** - Provide rollback options
5. **Document DNS requirements** - Custom domains need setup

---

## QUALITY CHECKLIST

Before completing deployment:

- [ ] Build validated successfully
- [ ] Deployment configuration generated
- [ ] Deployment executed without errors
- [ ] Live URL accessible
- [ ] Custom domain configured (if requested)
- [ ] DNS instructions provided (if custom domain)
- [ ] Deployment report generated
