---
type: concept
category: {pattern|convention|principle|style-guide}
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
  - "[[related-entity-or-concept]]"
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

# {Concept Name}

{2-3 sentence description of the concept.}

## Description

{Extended description: what this concept means, why it matters, how it applies.}

## Agent Context

```agent-context
triggers:
  - pattern: "*keyword*"
  - pattern: "path/related/**"
constraints:
  - "{Rule that implements this concept}"
  - "{Another rule}"
patterns:
  - name: "{pattern-name}"
    description: "Example implementation of this concept"
    template: |
      {Code example}
```

## Examples

### Example 1: {Title}

{Description of the example}

```
{Code example}
```

### Example 2: {Title}

{Description}

## Related Entities

- [[implementing-entity]] — Entity that implements this concept
- [[related-concept]] — Related concept

## Referencias

**Applies to:** [[entity-a]], [[entity-b]]
**Related concepts:** [[concept-x]]
