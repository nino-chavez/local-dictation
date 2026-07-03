# Generate Hybrid Documentation

Description: Creates documents that intentionally span multiple documentation layers, handling voice transitions appropriately. Use for executive summaries with technical appendices, architecture docs with operational runbooks, or other cross-layer needs.

Arguments:
- primary: Required. Primary layer: "architecture", "developer", "ops", "testing", "functional", "strategic", "user"
- secondary: Required. Secondary layer to incorporate
- topic: Required. The subject being documented
- ratio: (optional) Approximate split, e.g., "70-30" meaning 70% primary, 30% secondary. Defaults to "60-40".

---

You are executing a specialized documentation pipeline for hybrid documents. Read CLAUDE.md first, then read voice guides for BOTH specified layers:
- `docs/voice/[primary]-voice.md`
- `docs/voice/[secondary]-voice.md`

---

## HYBRID DOCUMENT PRINCIPLES

### Why Hybrid Documents Exist

Some deliverables legitimately need multiple voices:
- **Executive Brief + Technical Appendix**: Strategic voice for recommendations, Architecture voice for implementation details
- **Architecture Overview + Runbooks**: Architecture voice for design, Ops voice for operational procedures
- **User Guide + Reference**: Tutorial voice for learning, Reference voice for lookup tables
- **Strategic Assessment + Debt Inventory**: Strategic voice for executive summary, detailed debt items in technical format

### The Voice Transition Problem

Mixing voices within sections causes confusion. The solution: **explicit section boundaries with clear voice transitions**.

---

## THREE-PHASE PIPELINE

### PHASE 1: GENERATOR

*Planning the hybrid structure*

1. **Identify the primary audience** - Who is the main reader?
2. **Identify the secondary need** - Why do they need the other layer?
3. **Map the structure** - Which sections use which voice?

**Structure Template:**

```markdown
# [Document Title]

## Executive Summary / Overview
[PRIMARY VOICE - always lead with primary]

## [Primary Layer Sections]
[PRIMARY VOICE - bulk of content]

---

## Technical Details / Appendix / Reference
[SECONDARY VOICE - clearly separated]

---

## [More secondary sections if needed]
[SECONDARY VOICE]
```

### PHASE 2: REFINER

*Ensuring clean voice separation*

**For each section:**
1. Identify which voice applies
2. Apply that voice's patterns exclusively
3. Add transition markers between voices

**Transition Markers:**

```markdown
---

## Technical Appendix

> **Voice shift:** The following sections provide technical implementation
> details for engineering teams.

[Architecture/Ops/etc. voice content]
```

**Cross-reference, don't duplicate:**
- In executive sections: "See Technical Appendix for implementation details"
- In technical sections: "This implements the recommendation in Section 2"

### PHASE 3: VALIDATOR

*Checking voice integrity*

**Voice Contamination Check:**

For each section, verify:
- [ ] Uses ONLY the designated voice patterns
- [ ] No patterns from other voice leak in
- [ ] Transition is explicit (divider + marker)

**Common Contaminations to Catch:**

| Primary | Secondary | Common Leak | Fix |
|---------|-----------|-------------|-----|
| Strategic | Architecture | Technical jargon in exec summary | Move details to appendix |
| Architecture | Ops | Runbook checklists in design section | Separate into ops section |
| User Tutorial | Reference | Tables in learning flow | Link to reference, don't embed |
| Functional | Developer | Code examples in business rules | Remove code, describe behavior |

**Red Flags (Return to Phase 2):**
- [ ] Voice patterns mixed within a single section
- [ ] No clear visual/structural separation between voices
- [ ] Reader must switch mental modes mid-paragraph
- [ ] Same information duplicated in both voices

---

## COMMON HYBRID PATTERNS

### Pattern 1: Executive Brief + Technical Appendix

**Use when:** Leadership needs recommendations, engineers need implementation details

**Structure:**
```markdown
# [Topic] - Strategic Assessment

## Executive Summary
[STRATEGIC VOICE]
- Overall assessment
- Key recommendations
- Business impact

## Strategic Analysis
[STRATEGIC VOICE]
- Current state
- Risks and opportunities
- Recommended actions

---

## Technical Appendix

> For engineering teams implementing the recommendations above.

### Architecture Implications
[ARCHITECTURE VOICE]
- System changes required
- Component diagrams
- ADRs

### Implementation Tasks
[ARCHITECTURE VOICE]
- Detailed technical requirements
```

### Pattern 2: Architecture + Operations

**Use when:** System design needs operational procedures

**Structure:**
```markdown
# [System] Architecture & Operations

## Architecture Overview
[ARCHITECTURE VOICE]
- System design
- Component catalog
- Data flows

## Operational Model
[ARCHITECTURE VOICE]
- Deployment topology
- Scaling approach

---

## Operational Runbooks

> The following runbooks support day-to-day operations.

### Deployment Procedure
[OPS VOICE]
- Pre-deployment checklist
- Deployment steps
- Rollback procedures

### Incident Response
[OPS VOICE]
- Triage steps
- Escalation paths
```

### Pattern 3: User Guide + Reference

**Use when:** Users need both learning path and lookup tables

**Structure:**
```markdown
# [Feature] Guide

## Getting Started
[USER TUTORIAL VOICE]
- What you'll learn
- Prerequisites
- Step-by-step tutorial

## Common Tasks
[USER GUIDE VOICE]
- How to do X
- How to do Y

---

## Reference

> Quick lookup for settings and options.

### Configuration Options
[USER REFERENCE VOICE]
- Settings table
- Default values

### Keyboard Shortcuts
[USER REFERENCE VOICE]
- Shortcut table
```

---

## OUTPUT

Generate a hybrid document at `docs/[appropriate-location]/[topic].md` following the structure appropriate for the specified primary/secondary combination.

**Completion Checklist:**
- [ ] Primary voice used for majority of content
- [ ] Secondary voice clearly separated (visual divider + marker)
- [ ] No voice contamination within sections
- [ ] Cross-references connect the sections
- [ ] Document serves both audiences without confusion
