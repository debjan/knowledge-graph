# ADD Operation — Create Entity in Knowledge Graph

## When to Use This Operation

- User says "remember this", "save to memory", "create entity"
- After a non-trivial code change (new module, new class, new API endpoint)
- User explicitly describes an entity to add

## When NOT to Use This Operation

- User wants to query/load context (use QUERY operation)
- User wants to update existing entity (use UPDATE operation)
- User wants to delete entity (use DELETE operation)
- Change is trivial (formatting, white-space, comments)
- Entity already exists and hasn't changed

## Critical Rules

**RULE 1 — USER CONFIRMATION REQUIRED**
> Always present entity data to the user before writing. Never write without confirmation.

**RULE 2 — BIDIRECTIONAL REFERENCES**
> If creating an entity that references others, ensure bidirectional links are established.

**RULE 3 — HEALTH INITIALIZATION**
> Initialize health metadata for all new entities.

**RULE 4 — VISUALIZATION ARTIFACTS**
> When initializing a new project knowledge graph, ALWAYS create both `graph.base` (Obsidian Bases dashboard) and `graph-sequence.md` (Mermaid diagrams). These visualizations are essential for human navigation and understanding.

## Workflow

### Step 0: Resolve Paths

Resolve `{vault}` and `{project}`:

1. Check user message for explicit paths
2. Auto-discover vault path (common locations)
3. Extract project name from `{cwd}` basename or git repo
4. If ambiguous, ask user

Set `{graph_path}` = `{vault}/Memory/{project}/`

### Step 1: Check if Entity Exists

Before creating, check if entity already exists:

```
Read("{graph_path}/entities/{entity-name}.md")
```

**Error handling:** If `Read()` fails (permissions, I/O error):

- Report: "Cannot check for existing entity: {error}"
- Ask user: "Continue with new entity? [Yes/No]"
- If No: Abort operation

If entity exists:

- **If entity is healthy:** Offer UPDATE operation
- **If entity is stale:** Offer UPDATE or DELETE operation
- **If user wants different entity:** Proceed with new entity (different name)

### Step 2: Detect Non-Trivial Change

Use [change-detection.md](../helpers/change-detection.md) heuristics:

| Change Type        | Triggers ADD?             |
| ------------------ | ------------------------- |
| New file created   | Yes — candidate           |
| New class/function | Yes — candidate           |
| Import changes     | Yes — relationship change |
| New dependency     | Yes                       |
| Formatting only    | No                        |
| Renaming local var | No                        |

### Step 3: Extract Entity Metadata

Use [entity-extraction.md](../helpers/entity-extraction.md):

1. Parse file content
2. Identify entity type (module, class, function, api-endpoint)
3. Extract name, description, imports
4. Infer category and importance
5. Identify related entities

### Step 4: Prepare Entity Document

Use [entity-node.md](../templates/entity-node.md)

Initialize new metadata fields:

```yaml
usage:
  last_used: {today}
  use_count: 1
  last_auto_query: null
health:
  stale_files: []
  last_verified: {today}
  needs_update: false
  needs_delete: false
```

### Step 5: Confirm with User

Present the prepared entity:

```
I'll create this entity node:

**Name:** {entity-name}
**Type:** {type}
**Category:** {category}
**Importance:** {importance}
**Triggers:** {trigger-patterns}
**Related:** {related-entities}

Proceed? [Yes / No / Edit]
```

Wait for user confirmation.

### Step 6: Write Entity Document

1. Ensure directory exists:

```bash
mkdir -p "{graph_path}/entities/"
```

2. Write the document:

```
Write(file_path: "{graph_path}/entities/{entity-name}.md", content: {prepared_content})
```

**Error handling:** If `Write()` fails (disk full, permissions):

- Report: "Failed to write entity: {error}"
- Offer: "Retry / Change path / Abort"
- Do not report success if write failed

### Step 7: Maintain Bidirectional References

For each entity in `related`:

1. Read the related entity: `Read("{graph_path}/entities/{related}.md")`
2. Check if new entity is already in `related` field
3. If not, add it: `Edit(...)` to add `[[{entity-name}]]` to related
4. If related entity not found, warn: "Related entity [[{related}]] not found"

### Step 8: Report Results

```markdown
### ADD Complete

**Entity:** {name}
**Path:** `{graph_path}/entities/{name}.md`

**Frontmatter:**
- Type: {type}
- Category: {category}
- Importance: {importance}
- Related: {count} entities

**Bidirectional refs:**
- [[related-a]] ✓ (verified)
- [[related-b]] ✓ (verified)

**Metadata initialized:**
- usage: first use recorded
- health: verified
```

### Step 9: Create Index File

If this is a new project initialization (first entity in project):

Follow the workflow in [../templates/index-node.md](../templates/index-node.md):

1. Check if `index.md` exists: `Read("{graph_path}/index.md")`
2. If not exists, create from template with:
   - Quick stats (entity counts by type)
   - Architecture diagram (simplified Mermaid)
   - Browse by category links
   - Quick links organized by role
   - Search by concern table
3. If exists, prompt: "index.md already exists. [Skip] [Update]"

**Note:** Index file provides human-readable landing page for the knowledge graph.

### Step 10: Create Obsidian Bases Dashboard

Follow the workflow in [../bases/ops/ADD.md](../bases/ops/ADD.md) if it exists:

1. Check if `graph.base` exists: `Read("{graph_path}/graph.base")`
2. If not exists, read template and create: `Read("assets/bases/templates/graph-base.yaml")` → `Write("{graph_path}/graph.base")`
3. If exists, skip (preserve human customizations)

**Note:** This step is MANDATORY when initializing a new project. The `graph.base` file provides an interactive Obsidian Bases dashboard for navigating the knowledge graph.

### Step 11: Create Mermaid Diagrams

Follow the workflow in [../mermaid/ops/ADD.md](../mermaid/ops/ADD.md) if it exists:

1. Check if `graph-sequence.md` exists: `Read("{graph_path}/graph-sequence.md")`
2. If not exists, create initial sequence diagram with entity relationships
3. If exists, consider regenerating if relationships changed significantly

**Note:** This step is MANDATORY when initializing a new project. The `graph-sequence.md` file provides Mermaid diagrams showing data flow and entity interactions.

## Best Practices

- Always confirm before writing
- Check for existing entity before creating
- Offer UPDATE when entity exists
- Infer triggers from file paths (module structure)
- Keep descriptions concise (2-3 sentences)
- Extract constraints from code comments/docstrings
- Validate bidirectional refs before reporting success
- Warn if related entities not found, but proceed with ADD
- **ALWAYS create all three artifacts on project initialization:**
  - `graph.base` (Obsidian Bases dashboard)
  - `graph-sequence.md` (Mermaid diagrams)
  - `index.md` (Landing page)

## Quick Reference

| Artifact            | Location                     | Purpose                  | Created When |
| ------------------- | ---------------------------- | ------------------------ | ------------ |
| `index.md`          | `Memory/{project}/`          | Landing page             | First entity |
| `graph.base`        | `Memory/{project}/`          | Obsidian Bases dashboard | First entity |
| `graph-sequence.md` | `Memory/{project}/`          | Mermaid diagrams         | First entity |
| Entity nodes        | `Memory/{project}/entities/` | Knowledge nodes          | Each entity  |
