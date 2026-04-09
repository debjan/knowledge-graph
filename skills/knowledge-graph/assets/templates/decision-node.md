---
type: decision
name: {kebab-case-identifier}  # Programmatic identifier for API access
category: {adr|choice|tradeoff}
importance: {high|medium|low}
status: active
project: {project-name}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
agents:
  - {agent-model}
tags:
  - adr
  - {domain}
related:
  - "[[affected-entity-1]]"
  - "[[affected-entity-2]]"
usage:
  last_used: {YYYY-MM-DD}
  use_count: 1
  last_auto_query: null
health:
  stale_files: []
  last_verified: null
  needs_update: false
  needs_delete: false
changelog:
  - version: "1.0"
    date: {YYYY-MM-DD}
    changes: ["Initial creation"]
---

# ADR-{N}: {Decision Title}

**Status:** {Proposed|Accepted|Deprecated|Superseded}
**Date:** {YYYY-MM-DD}
**Decision Maker:** {Who made this decision}

## Context

{Describe the context and problem statement. What is the issue that is motivating this decision?}

## Decision

{Describe the decision that was made. Be concise and specific.}

## Consequences

### Positive

- {Benefit 1}
- {Benefit 2}

### Negative

- {Drawback 1}
- {Drawback 2}

### Neutral

- {Side effect 1}

## Alternatives Considered

| Option     | Pros    | Cons    | Why Rejected |
| ---------- | ------- | ------- | ------------ |
| {Option 1} | {pros}  | {cons}  | {reason}     |
| {Option 2} | {pros}  | {cons}  | {reason}     |

## Agent Context

```agent-context
triggers:
  - pattern: "*{keyword}*"
constraints:
  - "{Constraint derived from this decision}"
```

## Related Entities

- [[affected-entity]] — Entity affected by this decision
- [[related-decision]] — Related ADR

## References

**Supersedes:** [[ADR-{N-1}]] (if applicable)
**Superseded by:** [[ADR-{N+1}]] (if applicable)
