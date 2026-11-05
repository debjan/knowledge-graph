# Knowledge Graph Assets

Modular assets for the `knowledge-graph` skill. Detailed workflows, helpers, and templates load on-demand via progressive disclosure.

## Base Directory Structure

```
assets/
│   README.md
├───helpers/
│       change-detection.md — Non-trivial change heuristics
│       content-safety.md - Serialize untrusted content into YAML/Markdown safely
│       entity-extraction.md — Extract entity metadata from code
│       graph-traversal.md — Traverse related entities
│       keyword-extraction.md - Extract keywords from entity metadata
│       lifecycle-management.md - Manage entity lifecycle
│       relevance-scoring.md - Compute relevance scores for entities
│       safe-paths.md - Validate identifiers and paths before file operations
│       token-budget.md - Manage context size by counting tokens
├───ops/
│       ADD.md — Create entity workflow
│       DELETE.md — Remove entity workflow
│       QUERY.md — Read from graph workflow
│       RENAME.md — Rename entity workflow
│       SYNC.md — Synchronize entity workflow
│       UPDATE.md — Modify entity workflow
│       VERIFY.md — Verify entity workflow
├───specs/
│       agent-context-spec.md — Executable block schema specification
├───templates/
│       concept-node.md — Concept document template
│       constraint-node.md — Constraint document template
│       decision-node.md — ADR document template
│       entity-node.md — Entity document template
│       process-node.md — Process document template
│       index-node.md — Project landing page template
│       templates.md - Templates usage description
│       examples/ - One filled-in example per node type
├───mermaid/
│       README.md, ops/, templates/ (optional)
│       helpers/syntax-validation.md
└───bases/
        README.md, ops/, templates/graph-base.yaml (optional)
```

## Operation Loading

Helpers are **on demand**, not a fixed bundle. Start with the operation doc and the required helper; load the rest only when a step names it. That keeps a single ADD or QUERY from spending ~15-20 K tokens on reference material before it reads a single node.

| Operation  | Load These Assets                                                                                                                                                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ADD**    | `ops/ADD.md` → `helpers/safe-paths.md`, `helpers/content-safety.md`, `templates/<type>-node.md`, plus `helpers/entity-extraction.md` / `helpers/change-detection.md` when extracting or detecting |
| **UPDATE** | `ops/UPDATE.md` → `helpers/safe-paths.md`, `helpers/content-safety.md`, plus `helpers/entity-extraction.md` / `helpers/change-detection.md` when needed                                           |
| **DELETE** | `ops/DELETE.md` → `helpers/safe-paths.md` (required), `helpers/lifecycle-management.md` when the entity is high-importance                                                                        |
| **RENAME** | `ops/RENAME.md` → `helpers/safe-paths.md`                                                                                                                                                         |
| **SYNC**   | `ops/SYNC.md` → `helpers/safe-paths.md`, `helpers/content-safety.md`, `helpers/change-detection.md`, `helpers/lifecycle-management.md` (extraction only for NEW items)                            |
| **VERIFY** | `ops/VERIFY.md` → run `scripts/validate_graph.py` first; load `helpers/safe-paths.md` / `helpers/content-safety.md` only to explain a finding                                                     |
| **QUERY**  | `ops/QUERY.md` → `helpers/safe-paths.md` (required), then at most **one** of `relevance-scoring.md`, `graph-traversal.md`, `token-budget.md`, `keyword-extraction.md` when a step asks for it     |

### Optional features

| Operation  | Optional Features                                                                    |
| ---------- | ------------------------------------------------------------------------------------ |
| **ADD**    | `bases/ops/ADD.md` (if bases installed), `mermaid/ops/ADD.md` (if mermaid installed) |
| **UPDATE** | `bases/ops/UPDATE.md`, `mermaid/ops/UPDATE.md`                                       |
| **DELETE** | (visualizations auto-update)                                                         |
| **RENAME** | (visualizations auto-update)                                                         |
| **SYNC**   | (visualizations auto-update)                                                         |
| **VERIFY** | (read-only, no visuals)                                                              |
| **QUERY**  | -                                                                                    |

## Asset Descriptions

### Operations

- **ADD.md** - Workflow for creating new entity nodes
- **UPDATE.md** - Workflow for modifying existing entity nodes
- **SYNC.md** - Workflow for synchronizing existing entity nodes
- **DELETE.md** - Workflow for removing entity nodes with reference cleanup
- **RENAME.md** - Workflow for renaming entity nodes while preserving its history
- **VERIFY.md** - Workflow for verifying entities and presenting context briefing
- **QUERY.md** - Workflow for loading entities and presenting context briefing

### Helpers

- **change-detection.md** - Heuristics for detecting non-trivial code changes
- **content-safety.md** - Serialize untrusted content into YAML, Markdown, Mermaid, and Bases safely
- **entity-extraction.md** - Extract metadata (type, category, importance) from code files
- **graph-traversal.md** - Traverse related entities via wiki-links
- **keyword-extraction.md** - Extract keywords from entity metadata for relevance scoring
- **lifecycle-management.md** - Manage entity lifecycle (staleness detection, cleanup)
- **relevance-scoring.md** - Compute relevance scores for entities
- **safe-paths.md** - Validate identifiers and paths before any file operation
- **token-budget.md** - Manage context size by counting tokens

### Templates

- **entity-node.md** - Template for entity documents (modules, classes, functions)
- **concept-node.md** - Template for concept documents (patterns, conventions)
- **decision-node.md** - Template for ADR documents (architecture decisions)
- **constraint-node.md** - Template for constraint documents (gotchas, limitations)
- **process-node.md** - Template for process documents (workflows, algorithms)
- **index-node.md** - Template for project index/landing page

### Specifications

- **agent-context-spec.md** - Specification for `agent-context` executable blocks

### Bases (Optional)

- **bases/ops/ADD.md** - Create Obsidian Bases dashboard
- **bases/ops/UPDATE.md** - Update dashboard schema
- **bases/templates/graph-base.yaml** - Obsidian Bases template

### Mermaid (Optional)

- **mermaid/ops/ADD.md** - Create Mermaid diagrams
- **mermaid/ops/UPDATE.md** - Update diagrams
- **mermaid/templates/entity-interactions.md** - Sequence Diagram template
- **mermaid/templates/graph-relationships.md** - Relationship Graph template

Read [bases](./bases/README.md)
Read [mermaid](./mermaid/README.md)
