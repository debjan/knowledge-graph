# Knowledge Graph Assets

Modular assets for the `knowledge-graph` skill. Detailed workflows, helpers, and templates load on-demand via progressive disclosure.

## Base Directory Structure

```
assets/
│   README.md
├───helpers/
│       change-detection.md — Non-trivial change heuristics
│       entity-extraction.md — Extract entity metadata from code
│       graph-traversal.md — Traverse related entities
│       keyword-extraction.md - Extract keywords from entity metadata
│       lifecycle-management.md - Manage entity lifecycle
│       relevance-scoring.md - Compute relevance scores for entities
│       token-budget.md - Manage context size by counting tokens
├───ops/
│       ADD.md — Create entity workflow
│       DELETE.md — Remove entity workflow
│       QUERY.md — Read from graph workflow
│       RENAME.md — Rename entity workflow
│       SYNC.md — Synchronize entity workflow
│       UPDATE.md — Modify entity workflow
│       Verify.md — Verify entity workflow
├───specs/
│       agent-context-spec.md — Executable block schema specification
└───templates/
        concept-node.md — Concept document template
        constraint-node.md — Constraint document template
        decision-node.md — ADR document template
        entity-node.md — Entity document template
        process-node.md — Process document template
        templates.md - Templates usage description
```

## Operation Loading

| Operation  | Load These Assets                                                                                                |
| ---------- | ---------------------------------------------------------------------------------------------------------------- |
| **ADD**    | `ops/ADD.md` → `helpers/change-detection.md`, `helpers/entity-extraction.md`, `templates/entity-node.md`         |
| **UPDATE** | `ops/UPDATE.md` → `helpers/change-detection.md`, `helpers/entity-extraction.md`                                  |
| **DELETE** | `ops/DELETE.md` → `helpers/lifecycle-management.md`                                                              |
| **RENAME** | `ops/RENAME.md`                                                                                                  |
| **SYNC**   | `ops/SYNC.md` → `helpers/change-detection.md`, `helpers/entity-extraction.md`, `helpers/lifecycle-management.md` |
| **VERIFY** | `ops/VERIFY.md` → `helpers/lifecycle-management.md`                                                              |
| **QUERY**  | `ops/QUERY.md` → `helpers/graph-traversal.md`                                                                    |

### Optional features

| Operation  | Optional Features                                                                    |
| ---------- | ------------------------------------------------------------------------------------ |
| **ADD**    | `bases/ops/ADD.md` (if bases installed), `mermaid/ops/ADD.md` (if mermaid installed) |
| **UPDATE** | `bases/ops/UPDATE.md`, `mermaid/ops/UPDATE.md`                                       |
| **DELETE** | (visualizations auto-update)                                                         |
| **RENAME** | (visualizations auto-update)                                                         |
| **SYNC**   | (visualizations auto-update)                                                         |
| **VERIFY** | (read-only, no visuals)                                                              |
| **QUERY**  | —                                                                                    |

## Asset Descriptions

### Operations

- **ADD.md** — Workflow for creating new entity nodes
- **UPDATE.md** — Workflow for modifying existing entity nodes
- **SYNC.md** — Workflow for synchronizing existing entity nodes
- **DELETE.md** — Workflow for removing entity nodes with reference cleanup
- **RENAME.md** — Workflow for renaming entity nodes while preserving its history
- **VERIFY.md** — Workflow for verifying entities and presenting context briefing
- **QUERY.md** — Workflow for loading entities and presenting context briefing

### Helpers

- **change-detection.md** — Heuristics for detecting non-trivial code changes
- **entity-extraction.md** — Extract metadata (type, category, importance) from code files
- **graph-traversal.md** — Traverse related entities via wiki-links
- **keyword-extraction.md** — Extract keywords from entity metadata for relevance scoring
- **lifecycle-management.md** — Manage entity lifecycle (staleness detection, cleanup)
- **relevance-scoring.md** — Compute relevance scores for entities
- **token-budget.md** — Manage context size by counting tokens

### Templates

- **entity-node.md** — Template for entity documents (modules, classes, functions)
- **concept-node.md** — Template for concept documents (patterns, conventions)
- **decision-node.md** — Template for ADR documents (architecture decisions)
- **constraint-node.md** — Template for constraint documents (gotchas, limitations)
- **process-node.md** — Template for process documents (workflows, algorithms)
- **index-node.md** — Template for project index/landing page

### Specifications

- **agent-context-spec.md** — Specification for `agent-context` executable blocks

### Bases (Optional)

- **bases/ops/ADD.md** — Create Obsidian Bases dashboard
- **bases/ops/UPDATE.md** — Update dashboard schema
- **bases/templates/graph-base.yaml** — Obsidian Bases template

### Mermaid (Optional)

- **mermaid/ops/ADD.md** — Create Mermaid diagrams
- **mermaid/ops/UPDATE.md** — Update diagrams
- **mermaid/templates/entity-interactions.md** — Sequence Diagram template
- **mermaid/templates/graph-relationships.md** — Relationship Graph template

Read [bases](./bases/README.md)
Read [mermaid](./mermaid/README.md)
