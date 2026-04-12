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

**RULE 1 — VALIDATE ENTITY PROPERTIES**
> Entity properties must have valid YAML syntax.
> Use `yamllint` for verification if exists, or do manual YAML syntax check (look for missing quotes, incorrect indentation).

**RULE 2 — BIDIRECTIONAL REFERENCES**
> If creating an entity that references others, ensure bidirectional links are established.

**RULE 3 — HEALTH INITIALIZATION**
> Initialize health metadata for all new entities.

**RULE 4 — VISUALIZATION ARTIFACTS**
> When initializing a new project knowledge graph, ALWAYS create both `graph.base` (Obsidian Bases dashboard) and `graph-sequence.md`, `graph-relationships.md` (Mermaid diagrams). These visualizations are essential for human navigation and understanding.

## Workflow

### Step 0: Resolve Paths

Resolve `{vault}` and `{project}`:

1. Check user message for explicit paths
2. Auto-discover vault path (common locations: `~/Documents/Obsidian Vault`, `~/Obsidian`, `%USERPROFILE%/Documents/Obsidian Vault`, check environment variable `OBSIDIAN_VAULT`)
3. Extract project name from `{cwd}` basename or git repo
4. If ambiguous, ask user

Set `{graph_path}` = `{vault}/Memory/{project}/`

Load `obsidian-markdown` skill

### Step 1: Check if Entity Exists

Before creating, check if entity already exists:

```
Read("{graph_path}/entities/{entity-name}.md")
```

**Error:** Cannot check for existing entity
**Cause:** Read operation failed (permissions, I/O error)
**Options:** [Continue] [Abort]

**Action:**

- Continue: Proceed with creating new entity
- Abort: Cancel operation

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

### Step 2.5: Detect Node Type

Determine which node type to create based on user intent:

| Phrase / Signal                                        | Node Type      | Template           | Storage Path    |
| ------------------------------------------------------ | -------------- | ------------------ | --------------- |
| "entity", "module", "class", "service"                 | **Entity**     | entity-node.md     | `/entities/`    |
| "concept", "pattern", "convention", "principle"        | **Concept**    | concept-node.md    | `/concepts/`    |
| "decision", "ADR", "architecture decision", "we chose" | **Decision**   | decision-node.md   | `/decisions/`   |
| "constraint", "gotcha", "limitation", "warning"        | **Constraint** | constraint-node.md | `/constraints/` |
| "process", "workflow", "algorithm", "sequence"         | **Process**    | process-node.md    | `/processes/`   |

**Examples:**

- "Remember this **entity**..." → Creates entity node
- "Save this **pattern**..." → Creates concept node
- "Document this **decision**..." → Creates decision node
- "Note this **limitation**..." → Creates constraint node
- "Remember this **workflow**..." → Creates process node

**If unclear:** Ask user to clarify: "Is this an entity (code module), concept (pattern), decision (ADR), constraint (limitation), or process (workflow)?"

**Note:** All node types use the same ADD workflow, just different templates and storage folders. Based on detected type, use the appropriate template in Step 4.

### Step 3: Extract Entity Metadata

Use [entity-extraction.md](../helpers/entity-extraction.md):

1. Parse file content
2. Identify entity type (module, class, function, api-endpoint)
3. Extract name, description, imports
4. Infer category and importance
5. Identify related entities

### Step 4: Prepare Entity Document

Use appropriate template based on node type detected in Step 2.5:

| Node Type  | Template                                              |
| ---------- | ----------------------------------------------------- |
| Entity     | [entity-node.md](../templates/entity-node.md)         |
| Concept    | [concept-node.md](../templates/concept-node.md)       |
| Decision   | [decision-node.md](../templates/decision-node.md)     |
| Constraint | [constraint-node.md](../templates/constraint-node.md) |
| Process    | [process-node.md](../templates/process-node.md)       |

For entities (default):

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

1 Ensure [directories exists](#step-9-create-project-directory-structure)

2. Write the document:

```
Write(file_path: "{graph_path}/entities/{entity-name}.md", content: {prepared_content})
```

**Error:** Failed to write entity file
**Cause:** Disk full, permissions issue, or file locked
**Options:** [Retry] [Change path] [Abort]
**Note:**

- Retry: Attempt write again after checking storage/permissions
- Change path: Use alternate location for entity
- Abort: Cancel operation without writing
- Do not report success if write failed

### Step 7: Maintain Bidirectional References

**Two-phase approach (Recommended):**

1. **Collect Phase:** Build list of entities to update (with dry-run validation)
2. **Update Phase:** If all can be reached, apply all updates atomically
3. **On failure:** Rollback entity file, report which refs would have been created

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

### Step 9: Create Project Directory Structure

**When first entity in new project, create all folders:**

```bash
mkdir -p "{graph_path}/entities"
mkdir -p "{graph_path}/concepts"
mkdir -p "{graph_path}/decisions"
mkdir -p "{graph_path}/constraints"
mkdir -p "{graph_path}/processes"
```

**Why:** Graph traversal expects all folders to exist. Prevents errors in subsequent operations.

### Step 10: Create Index File

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

### Step 11: Create Obsidian Bases Dashboard

Follow the workflow in [../bases/ops/ADD.md](../bases/ops/ADD.md) **if bases feature is available**:

1. Check if bases feature is available: Verify `assets/bases/` directory exists
2. If not available, skip to Step 13 (bases is optional)
3. If available, check if `graph.base` exists: `Read("{graph_path}/graph.base")`
4. If not exists, read template and create: `Read("assets/bases/templates/graph-base.yaml")` → `Write("{graph_path}/graph.base")`
5. If exists, skip (preserve human customizations)

**Note:** This step is OPTIONAL. If the bases feature is installed (assets/bases/ exists), it provides an interactive Obsidian Bases dashboard for navigating the knowledge graph. Skip if bases was removed to keep the skill minimal.

### Step 12: Validate graph.base

**Requires:** `obsidian cli command`

After creating/updating `graph.base`, validate it:

```bash
obsidian base:views path="Memory/{project}/graph.base"
```

**Validation checks:**

- YAML structure valid
- All views parse correctly
- Filters syntax valid
- Formulas compile successfully

**If validation fails:**

1. **If yamllint available:** Check YAML syntax: `yamllint {graph_path}/graph.base`
2. **Otherwise:** Check YAML manually (look for missing quotes, incorrect indentation)
3. Fix template and regenerate
4. Re-validate before proceeding

### Step 13: Create Mermaid Diagrams

Follow the workflow in [../mermaid/ops/ADD.md](../mermaid/ops/ADD.md) **if mermaid feature is available**

If not available, skip this step

#### Step 13.1: Create Graph Relationships

- Check if `graph-relationships.md` exists: `Read("{graph_path}/graph-relationships.md")`
- If not exists, create relationship graph using [graph-relationships.md](../mermaid/templates/graph-relationships.md) template
- If exists, regenerate if structure changes

#### Step 13.2: Create Entity Relationships

- Check if `graph-sequence.md` exists: `Read("{graph_path}/graph-sequence.md")`
- If not exists, create initial sequence diagram using [entity-interactions.md](../mermaid/templates/entity-interactions.md) template
- If exists, consider regenerating if relationships changed significantly

## Best Practices

- Always confirm before writing
- Check for existing entity before creating
- Offer UPDATE when entity exists
- Infer triggers from file paths (module structure)
- Keep descriptions concise (2-3 sentences)
- Extract constraints from code comments/docstrings
- Validate bidirectional refs before reporting success
- Warn if related entities not found, but proceed with ADD
- **Recommended: Create available artifacts on project initialization (skip if optional features not installed):**
  - `index.md` (Landing page)
  - `graph.base` (Obsidian Bases dashboard) — Optional, requires bases feature
  - `graph-sequence.md` (Mermaid diagrams) — Optional, requires mermaid feature
  - `graph-relationships.md` (Mermaid diagrams) — Optional, requires mermaid feature

## Quick Reference

| Artifact                 | Location                     | Purpose                  | Created When |
| ------------------------ | ---------------------------- | ------------------------ | ------------ |
| `index.md`               | `Memory/{project}/`          | Landing page             | First entity |
| `graph.base`             | `Memory/{project}/`          | Obsidian Bases dashboard | First entity |
| `graph-sequence.md`      | `Memory/{project}/`          | Mermaid diagrams         | First entity |
| `graph-relationships.md` | `Memory/{project}/`          | Mermaid diagrams         | First entity |
| Entity nodes             | `Memory/{project}/entities/` | Knowledge nodes          | Each entity  |

## Optional Skill Dependencies

Use these skills when available:

| Skill               | Purpose                                              |
| ------------------- | ---------------------------------------------------- |
| `obsidian-markdown` | Proper Obsidian-flavored Markdown syntax in entities |
| `obsidian-bases`    | Dashboard view compatibility                         |

---

## See Also

**Related Operations:**

- [UPDATE](./UPDATE.md) — Modify existing entities
- [DELETE](./DELETE.md) — Remove entities
- [RENAME](./RENAME.md) — Rename/move entities
- [QUERY](./QUERY.md) — Load entity context

**Related Assets:**

- [entity-extraction.md](../helpers/entity-extraction.md) — Extract entity metadata
- [change-detection.md](../helpers/change-detection.md) — Detect non-trivial changes
- [entity-node.md](../templates/entity-node.md) — Entity document template
