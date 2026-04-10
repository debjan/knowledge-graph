---
name: knowledge-graph
description: >
 Proactive knowledge graph for AI agents — maintain entities, decisions, constraints, and patterns as linked markdown nodes.
 Auto-load context when working on matching files, auto-update after non-trivial changes.
 Features agent-proactive memory management with relevance scoring and lifecycle awareness.

auto_invoke:
 # ADD
 - "remember this"
 - "save to memory"
 - "this is important"
 - "add to knowledge graph"
 - "create entity"
 # UPDATE
 - "update the graph"
 - "update entity"
 - "refresh entity"
 # DELETE
 - "delete entity"
 - "remove entity"
 # RENAME
 - "rename entity"
 - "move entity"
 # QUERY
 - "load context for"
 - "what do we know about"
 - "check the graph for"
 - "what entities relate to"
 - "show me the knowledge graph"
 # Health Check
 - "check knowledge graph health"
 - "review stale entities"
 - "cleanup knowledge graph"
 # Mermaid
 - "generate mermaid"
 - "create mermaid diagram"
 - "visualize the graph"
 - "create sequence diagram"
 # Bases
 - "create bases"
 - "generate bases"
 - "create dashboard"

allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Knowledge Graph

## Assets

This skill uses a modular assets architecture. Detailed workflows, helpers, and templates are in the [assets](./assets/) directory:

- [operations](./assets/ops/) — ADD, UPDATE, DELETE, QUERY operation workflows
- [templates](./assets/templates/) — Node document templates
- [helpers](./assets/helpers/) — Change detection, entity extraction, graph traversal, relevance scoring, lifecycle management
- [mermaid](./assets/mermaid/) — Mermaid diagram generation (Sequence Diagram)
- [bases](./assets/bases/) — Obsidian Bases integration
- [specs](./assets/specs/) — agent-context block specification

See [README.md](./assets/README.md) for the directory index.

## Purpose

Proactive knowledge graph for AI agents. Maintains entities, decisions, constraints, and patterns as linked markdown nodes in Obsidian — auto-loading context when working on matching files, auto-updating after non-trivial changes.

**What it does:**

- **AUTO-QUERY**: Proactively load relevant context at invocation
- **ADD operation**: Create new entity nodes
- **UPDATE operation**: Modify existing entity nodes
- **DELETE operation**: Remove entity nodes with reference cleanup
- **QUERY operation**: Load relevant entities with relevance scoring and budget awareness
- **LIFECYCLE**: Detect stale entities, manage updates and deletions
- **INDEX**: Create human-readable landing page with quick stats and navigation
- **VISUALIZATIONS**: Create Obsidian Bases dashboards and Mermaid diagrams

**What a knowledge graph is:**

A collection of markdown documents representing entities, concepts, decisions, constraints, and processes — connected via Obsidian wiki-links (`[[entity-name]]`) and enriched with `agent-context` executable blocks. Includes `index.md` (human landing page), `graph.base` (Obsidian Bases dashboard), and `graph-sequence.md` (Mermaid diagrams) for navigation.

## Critical Rules

**RULE 1 — RESOLVE PATHS ONCE**

> Resolve `{vault}` and `{project}` once per session. Don't re-ask unless the user wants to change paths.

**RULE 2 — NO FABRICATION**

> Only report information that exists in entity nodes (QUERY) or was explicitly discussed (ADD/UPDATE). Never infer, guess, or complete missing data.

**RULE 3 — USER CONFIRMS BEFORE WRITE**

> In ADD or UPDATE operation, always present the gathered entity data to the user for review before writing. Never write without confirmation.

**RULE 4 — BIDIRECTIONAL REFERENCES**

> If entity A references entity B, then entity B MUST reference entity A. Maintain bidirectional wiki-links in the `related` frontmatter field.

**RULE 5 — ATOMIC OPERATIONS**

> ADD, UPDATE, DELETE, and RENAME operations must be atomic.
> If bidirectional reference updates fail, roll back or report partial success.
> Never leave the graph in an inconsistent state.

**RULE 6 — RESPECT TOKEN BUDGET**

> In QUERY operation, load context within token budget. Prioritize high-relevance entities. Summarize overflow.

**RULE 7 — VISUALIZATION ARTIFACTS**

> When initializing a new project knowledge graph, ALWAYS create both `graph.base` (Obsidian Bases dashboard) and `graph-sequence.md` (Mermaid diagrams). These visualizations are essential for human navigation and understanding.

## Operation Detection

| Operation      | Signals                                                                  | What It Does                                           |
| -------------- | ------------------------------------------------------------------------ | ------------------------------------------------------ |
| **AUTO-QUERY** | Session start                                                            | Proactively load context based on current work         |
| **ADD**        | "remember this", "save to memory", "create entity", "this is important"  | Create new entity nodes                                |
| **UPDATE**     | "update entity", "refresh entity", "update the graph"                    | Modify existing entity nodes                           |
| **DELETE**     | "delete entity", "remove entity"                                         | Remove entity nodes with reference cleanup             |
| **RENAME**     | "rename entity", "move entity"                                           | Rename entity while preserving history                 |
| **QUERY**      | "load context", "what do we know", "check graph", "show knowledge graph" | Load entities matching current work (within budget)    |
| **HEALTH**     | "check health", "review stale", "cleanup"                                | Scan for stale/unused entities, offer batch operations |

**Disambiguation**: If intent is unclear, ask:

> "Do you want me to **query** the graph (load context) or **add/update** to the graph (create/modify entities)?"

## Quick Start

### ADD Operation

Use when you want to create a new entity:

> Remember this authentication module.

**Assets to read now:** [ADD.md](./assets/ops/ADD.md)

### UPDATE Operation

Use when you want to modify an existing entity:

> Update entity auth-service.

**Assets to read now:** [UPDATE.md](./assets/ops/UPDATE.md)

### DELETE Operation

Use when you want to remove an entity:

> Delete entity old-module.

**Assets to read now:** [DELETE.md](./assets/ops/DELETE.md)

### QUERY Operation

Use when you need context for the work you're about to do:

> Load context for the payment service.

**Assets to read now:** [QUERY.md](./assets/ops/QUERY.md)

### Health Check

Use to review stale or unused entities:

> Check knowledge graph health.

**Assets to read now:** [lifecycle-management.md](./assets/helpers/lifecycle-management.md)

### Index Creation (Automatic)

Created automatically when initializing a new project knowledge graph:

> index.md — Human-readable landing page with quick stats and navigation

### Dashboards

**Assets to read now:** [bases](./assets/bases/README.md) if it exists, use for managing Obsidian Bases dashboard with tables, cards, and filters

**Assets to read now:** [mermaid](./assets/mermaid/README.md) if it exists, use for managing Mermaid sequence diagrams showing entity relationships

## Dependencies

| Dependency   | Required   | Purpose                                  |
| ------------ | ---------- | ---------------------------------------- |
| Obsidian     | Preferable | Markdown storage and graph visualization |
| ripgrep (rg) | Preferable | Proactive keyword-based retrieval        |
| yamllint     | Preferable | Validate yaml gnerated files             |

**Without ripgrep:** Falls back to glob-only matching. Proactive retrieval still works but less comprehensive.

**Required Skills (if available):**

- `@skill:obsidian-markdown` — Proper Obsidian-flavored Markdown syntax
- `@skill:obsidian-bases` — Dashboard view compatibility
- `@skill:obsidian-cli` - For interacting with Obsidian
