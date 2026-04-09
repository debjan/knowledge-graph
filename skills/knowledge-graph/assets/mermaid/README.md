# Knowledge Graph Mermaid

Mermaid diagram generation for the `knowledge-graph` skill. Creates portable, text-based visualizations from entity nodes.

## Directory Structure

```
mermaid/
├── README.md
├── ops/
│   ├── ADD.md — Mermaid generation workflow
│   └── UPDATE.md — Mermaid regeneration workflow
├── templates/
│   └── entity-interactions.md — Sequence Diagram template
└── helpers/
    └── syntax-validation.md — Mermaid syntax rules
```

## Generated Files

Per-project Mermaid diagram file in `Memory/{project}/`:

| File                | Diagram Type     | Purpose           |
| ------------------- | ---------------- | ----------------- |
| `graph-sequence.md` | Sequence Diagram | Interaction flows |

## Operation Loading

| Operation          | Load These Assets                                                  |
| ------------------ | ------------------------------------------------------------------ |
| **Mermaid ADD**    | `ops/ADD.md` → `templates/*.md`, `helpers/syntax-validation.md`    |
| **Mermaid UPDATE** | `ops/UPDATE.md` → `templates/*.md`, `helpers/syntax-validation.md` |

## Integration

Mermaid generation is triggered:

- Automatically after entity changes (ADD/UPDATE/DELETE operations)
- On explicit "generate mermaid" command

See [ADD operation](../ops/ADD.md) for the integration point.
