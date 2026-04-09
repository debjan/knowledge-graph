---
type: process
category: {workflow|algorithm|lifecycle|sequence}
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
  - "[[related-entity]]"
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

# {Process Name}

{One-line description of what this process does.}

## Description

{Detailed description: purpose, when it runs, who/what triggers it.}

## Steps

### Step 1: {Step Name}

{Description of this step}

- Input: {what comes in}
- Action: {what happens}
- Output: {what comes out}

### Step 2: {Step Name}

{Description}

- Input: {what comes in}
- Action: {what happens}
- Output: {what comes out}

### Step N: {Final Step}

{Description}

## Flow Diagram

```mermaid
flowchart LR
    A[Step 1] --> B[Step 2]
    B --> C[Step 3]
```

## Agent Context

```agent-context
triggers:
  - pattern: "*{keyword}*"
constraints:
  - "{Constraint for this process}"
patterns:
  - name: "{pattern-name}"
    template: |
      {Code pattern for this process}
```

## Error Handling

| Error     | Handling        |
| --------- | --------------- |
| {Error 1} | {How to handle} |
| {Error 2} | {How to handle} |

## Related Entities

- [[involved-entity]] — Entity involved in this process
- [[related-process]] — Related process

## Referencias

**Triggered by:** [[trigger-entity]]
**Produces:** [[output-entity]]
