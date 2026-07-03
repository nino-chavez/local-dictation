# Generate User Documentation

Description: Creates end-user documentation following the Diátaxis framework using a three-phase refinement pipeline. Transforms technical implementation into user-friendly guides, tutorials, and references.

Arguments:
- type: Required. One of: "tutorial", "guide", "reference", "explanation"
- feature: Required. The feature or capability to document.
- source: (optional) Specific source file to analyze for this feature.

---

You are executing a three-phase documentation pipeline. Read CLAUDE.md first for project context, then read `docs/voice/user-voice.md` for voice requirements.

---

## THREE-PHASE PIPELINE

### PHASE 1: GENERATOR
*Persona: Technical Writer creating initial draft*
- Identify the Diátaxis quadrant (tutorial, guide, reference, explanation)
- Execute the Analysis Process below
- Generate draft in appropriate template

### PHASE 2: REFINER
*Persona: User Experience Editor*
- Content matches single quadrant (no mixing)
- Steps are numbered, not bulleted
- Expected outcomes stated after each step
- Error scenarios covered with solutions

### PHASE 3: VALIDATOR
*Persona: QA reviewing against voice standards (see docs/voice/user-voice.md)*

**Anti-Patterns to Reject:**
| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| Tutorial without hands-on | Theory before practice | Lead with doing, explain as you go |
| Guide that teaches | "First, let's understand the concept..." | Assume knowledge, focus on task |
| Reference with persuasion | "You should use this when..." | Just describe what it is/does |
| Explanation with steps | "Step 1: Click..." | Explain concepts, link to guide for steps |
| "Simply" minimizing | "Simply configure the settings" | Remove minimizing language |

**Red Flags (Return to Phase 2):**
- [ ] Mixed Diátaxis quadrants in single document
- [ ] Code or API references visible to end users
- [ ] "Simply" or "just" before complex operations
- [ ] Steps without success criteria
- [ ] Missing prerequisites discovered mid-document

---

## Critical Rules

1. **Never use technical jargon** without explanation
2. **Never reference code, APIs, or implementation details**
3. **Always use "you" to address the reader**
4. **Always tell users what they'll achieve before explaining how**
5. **Always include what users should see/expect after each step**

## Persona

Imagine you're writing for someone who:
- Has never used this software before
- Is not a software developer
- Wants to accomplish a task, not learn technology
- May be frustrated or confused

---

## Type: Tutorial

**Purpose:** Learning-oriented, helps newcomers get started

**Location:** `docs/user/tutorials/[feature].md`

### Template

```markdown
# Getting Started with [Feature]

> In this tutorial, you'll learn how to [outcome]. By the end, you'll be able to [concrete achievement].

## What You'll Need

Before you begin, make sure you have:
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]

## Step 1: [Action Verb] [Object]

[One sentence explaining what we're doing and why]

1. [Specific instruction with exact UI element names]
2. [Next action]
3. [Next action]

**What you should see:** [Describe the expected result]

[Optional: Screenshot placeholder - describe what it would show]

## Step 2: [Action Verb] [Object]

[Continue pattern]

## Step 3: [Action Verb] [Object]

[Continue pattern]

## Congratulations!

You've successfully [achievement]. Here's what you learned:
- [Key concept 1]
- [Key concept 2]

## What's Next?

Now that you know the basics, you might want to:
- [Link to related tutorial]
- [Link to how-to guide for advanced usage]

## Troubleshooting

### [Common problem users might face]

**What you see:** [Symptom]

**Why it happens:** [Simple explanation]

**How to fix it:**
1. [Fix step 1]
2. [Fix step 2]
```

---

## Type: Guide (How-To)

**Purpose:** Task-oriented, helps users accomplish specific goals

**Location:** `docs/user/guides/[task].md`

### Template

```markdown
# How to [Accomplish Goal]

This guide shows you how to [specific outcome].

## Prerequisites

- [What users need before starting]

## Steps

### 1. [First action]

[Brief context if needed]

[Exact steps]

### 2. [Second action]

[Steps]

### 3. [Third action]

[Steps]

## Verification

To confirm everything worked:
1. [How to verify]
2. [What to look for]

## Common Issues

### [Issue 1]

**Solution:** [Quick fix]

### [Issue 2]

**Solution:** [Quick fix]

## Related

- [Link to related guide]
```

---

## Type: Reference

**Purpose:** Information-oriented, describes the machinery

**Location:** `docs/user/reference/[topic].md`

### Template

```markdown
# [Feature/Area] Reference

## Overview

[Brief description of what this reference covers]

## [Category 1]

| Item | Description | Values/Options |
|------|-------------|----------------|
| [Name] | [What it does] | [Allowed values] |
| [Name] | [What it does] | [Allowed values] |

## [Category 2]

### [Item Name]

**Description:** [What it is/does]

**Behavior:** [How it works]

**Default:** [Default value if applicable]

**Example:** [Practical example]

## Glossary

| Term | Definition |
|------|------------|
| [Term] | [Plain-language definition] |

## See Also

- [Related reference]
- [Related guide]
```

---

## Type: Explanation

**Purpose:** Understanding-oriented, provides context and background

**Location:** `docs/user/explanation/[concept].md`

### Template

```markdown
# Understanding [Concept]

## The Big Picture

[Start with context - why does this matter to the user?]

## How It Works

[Explain the concept in simple terms, using analogies if helpful]

Think of it like [relatable analogy].

## Key Concepts

### [Concept 1]

[Explanation]

### [Concept 2]

[Explanation]

## Common Scenarios

### When to use [Feature A] vs [Feature B]

**Use [A] when:** [Scenario]

**Use [B] when:** [Scenario]

## Frequently Asked Questions

### [Question users often ask]

[Answer]

### [Another common question]

[Answer]

## Learn More

- [Link to tutorial to try it]
- [Link to reference for details]
```

---

## Analysis Process

1. **Read the source code** for the specified feature
2. **Identify user actions** (what can users do?)
3. **Map to outcomes** (what do they achieve?)
4. **Extract validation rules** (what errors might they see?)
5. **Identify UI elements** referenced in code (buttons, forms, messages)
6. **Translate to user language**

## Translation Guide

| Code Concept | User Language |
|--------------|---------------|
| `onClick handler` | "Click the button" |
| `validation error` | "If you see a red message..." |
| `async operation` | "This may take a moment..." |
| `API endpoint` | [Don't mention - describe the action] |
| `state change` | "After you [action], you'll notice..." |
| `null/undefined` | "If nothing appears..." |

---

## Quality Checklist

Before finalizing:

- [ ] No code or technical terms without explanation
- [ ] All steps are testable by following exactly as written
- [ ] Expected outcomes described after each major step
- [ ] Error scenarios covered with solutions
- [ ] Links to related documentation included
- [ ] Appropriate Diataxis quadrant (don't mix types)
- [ ] Consistent voice (second person, active voice)
- [ ] Scannable format (headers, lists, tables)
