---
type: entity
category: {module|class|function|api-endpoint|component}
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
  - "[[related-entity-1]]"
  - "[[related-entity-2]]"
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

# {Entity Name}

{2-3 sentence description of the entity's purpose and role.}

## Description

{Extended description: what this entity does, its responsibilities, key features.}

## Agent Context

```agent-context
triggers:
  - pattern: "path/to/entity/**"
  - pattern: "*keyword*"
constraints:
  - "{Constraint 1: hard rule}"
  - "{Constraint 2: hard rule}"
patterns:
  - name: "{pattern-name}"
    description: "{When to use this pattern}"
    template: |
      {Code template as example}
checks:
  - "Run: {test-command}"
  - "Run: {lint-command}"
  - "Verify: {manual-check}"
```

## Implementation Files

- `{path/to/file.py}` — {Brief description}
- `{path/to/another.py}` — {Brief description}

## Related Entities

- [[related-entity-1]] — {Brief description of relationship}
- [[related-entity-2]] — {Brief description of relationship}

## Referencias

**Parent:** [[index]] (if exists)
**Depends on:** [[dependency-entity]]
**Used by:** [[consumer-entity]]

## Field Reference

### Frontmatter

| Field        | Required | Values                                                                    |
| ------------ | -------- | ------------------------------------------------------------------------- |
| `type`       | Yes      | `entity`                                                                  |
| `category`   | Yes      | `module`, `class`, `function`, `api-endpoint`, `component`                |
| `importance` | Yes      | `high`, `medium`, `low`                                                   |
| `status`     | Yes      | `active`, `deprecated`, `superseded`                                      |
| `project`    | Yes      | Project identifier (kebab-case)                                           |
| `created`    | Yes      | ISO date (YYYY-MM-DD)                                                     |
| `updated`    | Yes      | ISO date (YYYY-MM-DD)                                                     |
| `agents`     | Yes      | List of AI models that created/modified                                   |
| `tags`       | Yes      | Up to 10 relevant tags                                                    |
| `related`    | Yes      | Wiki-links to related entities                                            |
| `usage`      | Yes      | Usage tracking: `{last_used, use_count, last_auto_query}`                 |
| `health`     | Yes      | Entity health: `{stale_files, last_verified, needs_update, needs_delete}` |
| `changelog`  | Yes      | Version history                                                           |

### Usage Fields

| Field             | Type      | Description                                       |
| ----------------- | --------- | ------------------------------------------------- |
| `last_used`       | date      | Date entity was last loaded in a QUERY            |
| `use_count`       | integer   | Total times entity has been loaded                |
| `last_auto_query` | date/null | Date entity was last auto-loaded at session start |

### Health Fields

| Field           | Type      | Description                                       |
| --------------- | --------- | ------------------------------------------------- |
| `stale_files`   | array     | List of implementation files that no longer exist |
| `last_verified` | date/null | Date of last health verification                  |
| `needs_update`  | boolean   | Flag indicating entity content may be outdated    |
| `needs_delete`  | boolean   | Flag suggesting entity should be removed          |

### agent-context Block

| Field        | Required | Description                         |
| ------------ | -------- | ----------------------------------- |
| `triggers`   | Yes      | File patterns that load this entity |
| `constraints`| No       | Hard rules (MUST follow)            |
| `patterns`   | No       | Code templates (SHOULD use)         |
| `checks`     | No       | Commands to run after changes       |
