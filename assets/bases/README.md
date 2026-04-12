# Knowledge Graph Bases

Obsidian Bases integration for the `knowledge-graph` skill. Creates and maintains per-project dashboard files for knowledge graph visualization.

## Directory Structure

```
bases/
├── README.md
├── ops/
│   ├── ADD.md — Base creation workflow
│   └── UPDATE.md — Schema sync workflow
└── templates/
    └── graph-base.yaml — Per-project base template
```

## Generated Files

Per-project base file:

| File         | Location                      | Purpose                                                                   |
| ------------ | ----------------------------- | ------------------------------------------------------------------------- |
| `graph.base` | `memory/{project}/graph.base` | Per-project dashboard with entity overview, health status, activity views |

## Operation Loading

| Operation       | Load These Assets                                 |
| --------------- | ------------------------------------------------- |
| **Base ADD**    | `./ops/ADD.md` → `./templates/graph-base.yaml`    |
| **Base UPDATE** | `./ops/UPDATE.md` → `./templates/graph-base.yaml` |

## Integration

Base creation is triggered:

- On first entity creation in a new project (creates `graph.base`)
- On explicit "create base" command

See [ADD operation](../ops/ADD.md) for the integration point.
