# Knowledge Graph Skill

A proactive knowledge graph system for AI agents that maintains entities, decisions, constraints, and patterns as linked markdown nodes in Obsidian.

## Features

- **AUTO-QUERY**: Proactively load relevant context at session start
- **ADD/UPDATE/DELETE/RENAME**: Manage entity nodes with reference cleanup
- **QUERY**: Load relevant entities with relevance scoring and budget awareness
- **LIFECYCLE**: Detect stale entities, manage updates and deletions

## Optional Features

The following features are optional and can be safely deleted if not needed:

- **Mermaid diagrams** (`assets/mermaid/`) - Sequence and relationship diagram generation
- **Obsidian Bases** (`assets/bases/`) - Dashboard views

To remove: delete the respective directories under `knowledge-graph/assets/`.

## Installation

Clone as a skill for AI agents:

```bash
mkdir -p ~/.agents/skills
git clone https://gitlab.com/dejan.stojkovic/knowledge-graph-skill ~/.agents/skills/knowledge-graph
```

## Usage

The skill auto-loads when working on matching files.

## License

MIT
