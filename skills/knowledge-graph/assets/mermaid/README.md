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

### Step 10: Regenerate Mermaid Diagrams

After entity is written, automatically regenerate Mermaid diagrams:

For initial creation, follow [ADD workflow](../ops/ADD.md).
For regeneration after entity changes, follow [UPDATE workflow](../ops/UPDATE.md):

1. Check if `graph-sequence.md` exists
2. If yes: Regenerate sequence diagram with timestamp
3. If no: Prompt: "Create Mermaid visualizations? [Yes] [No]"

**Note:** Mermaid diagrams are regenerated automatically on ADD/UPDATE/DELETE operations to stay in sync with the knowledge graph.

### Step 11: Create Index File

If this is a new project initialization (first entity in project):

Follow the workflow in [../templates/index-node.md](../templates/index-node.md):

1. Check if `index.md` exists: `Read("{graph_path}/index.md")`
2. If not exists, create from template
3. Include:
   - Quick stats (entity counts by type)
   - Architecture diagram (simplified Mermaid)
   - Browse by category links
   - Quick links organized by role
   - Search by concern table
4. If exists, prompt: "index.md already exists. [Skip] [Update]"

**Note:** Index file provides human-readable landing page for the knowledge graph.
