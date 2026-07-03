# Initialize Documentation System

Description: Bootstrap comprehensive documentation infrastructure for any existing project. Detects stack, generates CLAUDE.md, creates doc structure, and installs all documentation skills.

Arguments:
- target: (optional) Path to the project root. Defaults to current directory.

---

You are a Documentation Architect performing a full bootstrap of the Autonomous Knowledge Synthesis system. Execute the following phases precisely.

## Phase 0: Project Detection

Analyze the project at `$target` (or current directory if not specified).

### Step 0.1: Detect Project Type
Run these commands and analyze the results:
```
tree -L 2 -I 'node_modules|vendor|.git|dist|build|__pycache__|.venv|venv' $target
```

Classify as one of:
- **Monolith**: Single deployable unit
- **Microservices**: Multiple service directories with independent configs
- **Monorepo**: Multiple packages/apps with shared tooling (look for workspaces)
- **Library**: Publishable package (look for main/module in package.json or setup.py)

### Step 0.2: Detect Tech Stack
Check for these indicator files and extract versions where possible:

| Category | Indicators | Extract |
|----------|-----------|---------|
| **Runtime** | `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `Gemfile`, `pom.xml`, `build.gradle` | Language + version |
| **Framework** | `next.config.*`, `nuxt.config.*`, `angular.json`, `django`, `flask`, `fastapi`, `rails`, `spring` | Framework name |
| **Database** | `prisma/`, `drizzle.config.*`, `schema.sql`, `migrations/`, `docker-compose.yml` (look for db images) | DB type |
| **Infrastructure** | `terraform/`, `pulumi/`, `cdk/`, `cloudformation/`, `kubernetes/`, `helm/` | IaC tool |
| **CI/CD** | `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `bitbucket-pipelines.yml` | CI platform |
| **Containerization** | `Dockerfile`, `docker-compose.yml`, `compose.yaml` | Container tech |

### Step 0.3: Detect Existing Documentation
Check for:
- `README.md` (root level)
- `docs/` directory
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `*.md` files in root
- Existing `CLAUDE.md`

---

## Phase 1: Generate CLAUDE.md

Create `$target/CLAUDE.md` with the detected information:

```markdown
# Project: [Detected project name from package.json/go.mod/etc or directory name]

## Identity
[One sentence describing what this project does - infer from README or main entry points]

**Type:** [Monolith | Microservices | Monorepo | Library]

## Tech Stack
- **Language:** [Detected language + version]
- **Framework:** [Detected framework]
- **Database:** [Detected DB or "None detected"]
- **Infrastructure:** [Detected IaC or "None detected"]
- **CI/CD:** [Detected CI platform]

## Documentation Standards
- Format: GitHub-Flavored Markdown
- Diagrams: Mermaid.js (embedded in Markdown)
- Structure: Diataxis framework for user docs
- Location: `docs/` directory

## Key Directories
[List the main directories and their purposes based on structure analysis]

## Exclusions
Ignore these directories when analyzing code:
- node_modules/
- vendor/
- .git/
- dist/
- build/
- __pycache__/
- .venv/
- venv/
- coverage/
- .next/
- .nuxt/

## Commands
[Detect from package.json scripts, Makefile, or equivalent]
- **Install:** [detected command]
- **Dev:** [detected command]
- **Build:** [detected command]
- **Test:** [detected command]
- **Lint:** [detected command]

## Documentation Skills
Available commands after initialization:
- `/doc-architecture` - Generate architecture documentation
- `/doc-developer` - Generate developer onboarding guide
- `/doc-ops` - Generate DevOps and infrastructure docs
- `/doc-testing` - Generate testing strategy docs
- `/doc-functional` - Extract business logic documentation
- `/doc-strategic` - Generate tech debt audit and roadmap
- `/doc-user [feature]` - Generate user-facing documentation
- `/doc-audit` - Run documentation coverage audit
```

---

## Phase 2: Create Documentation Structure

Create the following directory structure at `$target/docs/`:

```
docs/
├── architecture/
│   ├── README.md           # Architecture overview (to be generated)
│   ├── decisions/          # ADRs go here
│   │   └── README.md       # ADR index
│   └── diagrams/           # Mermaid source files
│       └── README.md       # Diagram index
├── developer/
│   ├── README.md           # Developer guide (to be generated)
│   ├── setup.md            # Environment setup
│   └── contributing.md     # Contribution guidelines
├── ops/
│   ├── README.md           # Ops overview
│   ├── infrastructure.md   # Infrastructure topology
│   ├── deployment.md       # Deployment procedures
│   └── runbooks/           # Operational runbooks
│       └── README.md
├── testing/
│   ├── README.md           # Testing strategy
│   └── coverage.md         # Coverage analysis
├── functional/
│   ├── README.md           # Functional specs index
│   └── business-rules/     # Extracted business logic
│       └── README.md
├── strategic/
│   ├── README.md           # Strategic overview
│   ├── tech-debt.md        # Technical debt audit
│   └── roadmap.md          # Remediation roadmap
└── user/
    ├── README.md           # User docs index
    ├── tutorials/          # Diataxis: Learning
    │   └── README.md
    ├── guides/             # Diataxis: How-to
    │   └── README.md
    ├── reference/          # Diataxis: Information
    │   └── README.md
    └── explanation/        # Diataxis: Understanding
        └── README.md
```

For each README.md, create a minimal placeholder with:
```markdown
# [Section Name]

> This documentation is auto-generated by the Autonomous Knowledge Synthesis system.
> Last updated: [current date]

## Status: Pending Generation

Run the appropriate documentation skill to generate this content:
- `/doc-[skill-name]`

## Contents

[To be generated]
```

---

## Phase 3: Install Documentation Skills

Check if `$target/.claude/commands/` exists. If not, create it.

Copy all documentation skills to `$target/.claude/commands/`:
- `doc-architecture.md`
- `doc-developer.md`
- `doc-ops.md`
- `doc-testing.md`
- `doc-functional.md`
- `doc-strategic.md`
- `doc-user.md`
- `doc-audit.md`

---

## Phase 4: Initial Discovery Audit

After setup, run a quick discovery audit and output a summary:

### Component Inventory
List the major components/modules discovered with line counts:
```
find $target -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" | head -50
```

### Documentation Priority Matrix
Based on the discovery, output a prioritized list:

| Priority | Component | Reason | Skill to Run |
|----------|-----------|--------|--------------|
| 1 | [highest complexity/most critical] | [reason] | `/doc-architecture` |
| 2 | ... | ... | ... |

### Recommended Next Steps
1. Review generated `CLAUDE.md` and adjust if needed
2. Run `/doc-architecture` first to establish system overview
3. Run `/doc-developer` to enable team onboarding
4. Continue with other skills as needed

---

## Output Summary

After completing all phases, output:

```
╔══════════════════════════════════════════════════════════════════╗
║  Documentation System Initialized                                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Project: [name]                                                  ║
║  Type: [type]                                                     ║
║  Stack: [primary language/framework]                              ║
╠══════════════════════════════════════════════════════════════════╣
║  Created:                                                         ║
║  ✓ CLAUDE.md (project configuration)                              ║
║  ✓ docs/ (documentation structure)                                ║
║  ✓ .claude/commands/ (8 documentation skills)                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Next: Run /doc-architecture to generate system overview          ║
╚══════════════════════════════════════════════════════════════════╝
```
