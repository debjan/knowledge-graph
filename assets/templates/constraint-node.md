---
type: constraint
name: {kebab-case-identifier}  # Programmatic identifier for API access
category: {gotcha|limitation|warning|edge-case}
importance: {high|medium|low}
status: active
project: {project-name}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
agents:
  - {agent-model}
tags:
  - {tag1}
  - {tag2}
related:
  - "[[affected-entity]]"
usage:
  last_used: {YYYY-MM-DD}
  use_count: 1
  last_auto_query: null
health:
  stale_files: []  # N/A for constraints (no implementation files)
  last_verified: null
  needs_update: false
  needs_delete: false
changelog:
  - version: "1.0"
    date: {YYYY-MM-DD}
    changes: ["Initial creation"]
---

# {Constraint Name}

{One-line summary of the constraint.}

## Description

{Detailed description: what is the constraint, why it exists, what happens if violated.}

## Impact

**Severity:** {Critical|High|Medium|Low}
**Affected areas:** {List of affected modules/features}

## Root Cause

{Why this constraint exists. Is it a technical limitation, business rule, or discovered issue?}

## Workaround

{If there's a workaround, describe it here. If not, state "No workaround available."}

## Agent Context

```agent-context
triggers:
  - pattern: "*{keyword}*"
constraints:
  - "{The constraint rule}"
  - "{Related constraint}"
```

## Examples

### Example: Violation

{What happens when this constraint is violated}

```
{Code example of violation}
```

### Example: Correct Usage

{How to work within this constraint}

```
{Code example of correct usage}
```

## Related Entities

- [[affected-entity]] — Entity constrained by this
- [[related-constraint]] — Related constraint

## References

**Applies to:** [[entity-a]], [[entity-b]]
