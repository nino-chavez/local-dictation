# Documentation Coverage Audit

Description: Analyzes existing documentation against codebase to identify gaps, outdated content, and prioritized improvement opportunities.

Arguments:
- scope: (optional) "full" for complete audit, "quick" for high-level overview. Defaults to "quick".

---

You are a Documentation Quality Auditor performing a comprehensive coverage analysis. Read CLAUDE.md first for project context.

## Audit Protocol

### Pass 1: Documentation Inventory

Scan for all documentation:
```bash
find . -name "*.md" -not -path "./node_modules/*" -not -path "./.git/*"
```

Categorize by type:
- Root docs (README, CONTRIBUTING, etc.)
- Architecture docs
- Developer docs
- API docs
- User docs
- Inline docs (code comments)

### Pass 2: Codebase Inventory

Map documentable entities:

| Entity Type | How to Find | Expected Docs |
|-------------|-------------|---------------|
| Entry points | `main.*`, `index.*`, `app.*` | README |
| Public APIs | Exported functions/classes | JSDoc/docstrings |
| Services | `*Service.*`, `*Controller.*` | Module README |
| Config | `*.config.*`, `.env.*` | Environment docs |
| Scripts | `package.json` scripts, `Makefile` | Usage docs |

### Pass 3: Coverage Analysis

Compare documentation against code:

1. **What's documented but outdated?**
   - Compare file modification dates
   - Check for referenced files that no longer exist
   - Look for deprecated features still documented

2. **What's implemented but undocumented?**
   - New features (recent commits) without docs
   - Public APIs without comments
   - Configuration without explanation

3. **What's partially documented?**
   - Incomplete READMEs
   - Missing sections (setup, usage, examples)
   - Placeholder content

### Pass 4: Quality Assessment

For each documentation file, evaluate:

| Criterion | Score 1-5 | Indicators |
|-----------|-----------|------------|
| Accuracy | | Does it match current code? |
| Completeness | | Are all aspects covered? |
| Clarity | | Is it understandable? |
| Currency | | Recently updated? |
| Accessibility | | Easy to find and navigate? |

---

## Output: docs/audit-report.md

```markdown
# Documentation Audit Report

> Generated: [date]
> Scope: [full/quick]
> Auditor: Autonomous Knowledge Synthesis

## Executive Summary

### Documentation Health Score: [X/100]

| Dimension | Score | Status |
|-----------|-------|--------|
| Coverage | [X/25] | [Complete/Partial/Missing] |
| Accuracy | [X/25] | [Current/Outdated/Incorrect] |
| Completeness | [X/25] | [Thorough/Adequate/Sparse] |
| Accessibility | [X/25] | [Excellent/Good/Poor] |

### Key Findings

1. **[Most Critical Gap]**
2. **[Second Finding]**
3. **[Third Finding]**

---

## Coverage Matrix

### Documentation by Layer

| Layer | Expected | Exists | Status | Priority |
|-------|----------|--------|--------|----------|
| Architecture | `docs/architecture/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| Developer | `docs/developer/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| DevOps | `docs/ops/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| Testing | `docs/testing/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| Functional | `docs/functional/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| Strategic | `docs/strategic/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |
| User Docs | `docs/user/` | [Yes/No/Partial] | [Status] | [P1/P2/P3] |

### Critical Components

| Component | Location | Has README | Has API Docs | Status |
|-----------|----------|------------|--------------|--------|
| [Name] | `src/services/auth/` | [Yes/No] | [Yes/No] | [Gap] |
| [Name] | `src/services/orders/` | [Yes/No] | [Yes/No] | [Good] |

---

## Gap Analysis

### Missing Documentation

| Priority | Component | Missing | Skill to Run |
|----------|-----------|---------|--------------|
| P1 | Core API | Architecture overview | `/doc-architecture` |
| P1 | Onboarding | Developer setup guide | `/doc-developer` |
| P2 | Deployment | CI/CD documentation | `/doc-ops` |

### Outdated Documentation

| File | Last Updated | Code Changed | Drift Level |
|------|--------------|--------------|-------------|
| `docs/api/auth.md` | 2023-06-15 | 2024-01-20 | High |
| `README.md` | 2023-12-01 | 2024-02-01 | Medium |

### Incomplete Documentation

| File | Missing Sections |
|------|------------------|
| `README.md` | Prerequisites, Troubleshooting |
| `docs/developer/setup.md` | Environment variables, Verification |

---

## Quality Assessment

### High Quality Docs

| File | Strengths |
|------|-----------|
| [File] | Clear structure, current, complete |

### Needs Improvement

| File | Issues | Recommendation |
|------|--------|----------------|
| [File] | Missing examples | Add code samples |
| [File] | Outdated screenshots | Update with current UI |

---

## Recommendations

### Immediate Actions (This Week)

1. **[Action]** - [Brief justification]
   - Skill: `/doc-[skill]`
   - Effort: [Low/Medium/High]

2. **[Action]**
   - Skill: `/doc-[skill]`
   - Effort: [Low/Medium/High]

### Short-term Actions (This Month)

3. **[Action]**
4. **[Action]**

### Long-term Improvements

5. **[Action]**
6. **[Action]**

---

## Maintenance Recommendations

### Documentation Hygiene

- [ ] Add documentation updates to PR checklist
- [ ] Set up doc freshness monitoring
- [ ] Establish doc review schedule

### Suggested Cadence

| Doc Type | Review Frequency | Owner |
|----------|-----------------|-------|
| Architecture | Quarterly | Tech Lead |
| Developer | On code changes | Team |
| API Reference | On API changes | Team |
| User Guides | On feature changes | Product |

---

## Appendix: Full Inventory

### All Documentation Files

| Path | Type | Lines | Last Modified |
|------|------|-------|---------------|
| `README.md` | Root | [X] | [Date] |
| `docs/architecture/README.md` | Architecture | [X] | [Date] |
| ... | ... | ... | ... |

### Undocumented Entry Points

| File | Type | Priority |
|------|------|----------|
| `src/services/PaymentService.ts` | Service | High |
| ... | ... | ... |
```

---

## Completion Output

After audit, provide:

```
╔══════════════════════════════════════════════════════════════════╗
║  Documentation Audit Complete                                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Health Score: [X/100]                                           ║
║  Coverage: [X%]                                                   ║
║  Gaps Found: [X]                                                  ║
║  Outdated Docs: [X]                                               ║
╠══════════════════════════════════════════════════════════════════╣
║  Top Priority:                                                    ║
║  1. [Action] - run /doc-[skill]                                   ║
║  2. [Action] - run /doc-[skill]                                   ║
║  3. [Action] - run /doc-[skill]                                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Report: docs/audit-report.md                                     ║
╚══════════════════════════════════════════════════════════════════╝
```
