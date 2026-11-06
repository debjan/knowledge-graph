# Knowledge Graph Skill

A proactive knowledge graph system for AI agents that maintains entities, decisions, constraints, and patterns as linked markdown nodes in Obsidian.

## Features

- **AUTO-QUERY**: Load relevant context when the skill is invoked for a task
- **ADD/UPDATE/DELETE/RENAME/SYNC/VERIFY**: Manage entity nodes with reference cleanup
- **QUERY**: Load relevant entities with relevance scoring and budget awareness
- **LIFECYCLE**: Detect stale entities, manage updates and deletions
- **VERIFY**: Ten graph integrity checks, nine through the bundled `validate_graph.py`

## Optional Features

The following features are optional and can be safely deleted if not needed:

- **Mermaid diagrams** (`assets/mermaid/`) - Sequence and relationship diagram generation
- **Obsidian Bases** (`assets/bases/`) - Dashboard views

To remove: delete the respective directories under `knowledge-graph/assets/`. The skill works without them; see the Compatibility section in [SKILL.md](./SKILL.md).

## Requirements

Nothing beyond file read/write/search is required. Optional: Python 3.9+ for the VERIFY validator, Obsidian for Bases, ripgrep for faster keyword search.

## Installation

Clone the repository in your agents skills folder.

## Usage

There is no `generate graph` command - that was documented but never implemented. The skill **is** the workflow; initialize a project by asking for the first node:

```
> Add the auth module to the knowledge graph
```

That runs the ADD operation, which creates the folder structure, the first entity, `{project}.index.md`, the Bases dashboard and the Mermaid diagrams (Steps 8-15). Subsequent work is driven by the operation names: `add`, `update`, `delete`, `rename`, `query`, `sync`, `verify`.

<img width="1550" height="1005" alt="image" src="https://github.com/user-attachments/assets/3db3351f-4510-4e95-a968-46af281158ce" />
