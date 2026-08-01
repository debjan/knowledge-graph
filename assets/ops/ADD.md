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

### RULE 1: VALIDATE ENTITY PROPERTIES

> Entity properties must have valid YAML syntax.

### RULE 2: BIDIRECTIONAL REFERENCES

> If creating an entity that references others, ensure bidirectional links are established.

### RULE 3: HEALTH INITIALIZATION

> Initialize health metadata for all new entities.

### RULE 4: VISUALIZATION ARTIFACTS

> When initializing a new project knowledge graph, **attempt to create**:
>
> - `{project}.graph.base` (Obsidian Bases dashboard)
> - `{project}.graph-sequence.md`, `{project}.graph-relationships.md` (Mermaid diagrams).
>
> These visualizations are essential for human navigation and understanding.

## Workflow

### Step 1: Resolve Paths

Resolve `{vault}`, `{memory}` and `{project}`:

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

Set `{graph_path}` = `{vault}/{memory}/{project}/`

Load `obsidian-markdown` skill

### Step 2: Check if Entity Exists

Before creating, check if entity already exists:

```
Read("{graph_path}/entities/{project}.{entity-name}.md")
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

### Step 3: Detect Non-Trivial Change

Use [change-detection.md](../helpers/change-detection.md) heuristics:

| Change Type        | Triggers ADD?             |
| ------------------ | ------------------------- |
| New file created   | Yes — candidate           |
| New class/function | Yes — candidate           |
| Import changes     | Yes — relationship change |
| New dependency     | Yes                       |
| Formatting only    | No                        |
| Renaming local var | No                        |

### Step 4: Detect Node Type

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

### Step 5: Extract Entity Metadata

Use [entity-extraction.md](../helpers/entity-extraction.md):

1. Parse file content
2. Identify entity type (module, class, function, api-endpoint)
3. Extract name, description, imports
4. Infer category and importance
5. Identify related entities

### Step 6: Prepare Entity Document

Use appropriate template based on node type detected in Step 4:

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

### Step 7: Confirm with User

Present the prepared entity:

```
I'll create this entity node:

**Name:** {project}.{entity-name}
**Type:** {type}
**Category:** {category}
**Importance:** {importance}
**Triggers:** {trigger-patterns}
**Related:** {related-entities}

Proceed? [Yes / No / Edit]
```

Wait for user confirmation.

### Step 8: Write Entity Document

1 Ensure [directories exists](#step-11-create-project-directory-structure)

2. Write the document:

```
Write(file_path: "{graph_path}/entities/{project}.{entity-name}.md", content: {prepared_content})
```

**Error:** Failed to write entity file
**Cause:** Disk full, permissions issue, or file locked
**Options:** [Retry] [Change path] [Abort]
**Note:**

- Retry: Attempt write again after checking storage/permissions
- Change path: Use alternate location for entity
- Abort: Cancel operation without writing
- Do not report success if write failed

### Step 9: Maintain Bidirectional References

**Two-phase approach (Recommended):**

1. **Collect Phase:** Build list of entities to update (with dry-run validation)
2. **Update Phase:** If all can be reached, apply all updates atomically
3. **On failure:** Rollback entity file, report which refs would have been created

For each entity in `related`:

1. Read the related entity: `Read("{graph_path}/entities/{project}.{related}.md")`
2. Check if new entity is already in `related` field
3. If not, add it: `Edit(...)` to add `[[{project}.{entity-name}]]` to related
4. If related entity not found, warn: "Related entity [[{project}.{related}]] not found"

### Step 10: Report Results

```
### ADD Complete

**Entity:** {project}.{name}
**Path:** `{graph_path}/entities/{project}.{name}.md`

**Frontmatter:**
- Type: {type}
- Category: {category}
- Importance: {importance}
- Related: {count} entities

**Bidirectional refs:**
- [[{project}.related-a]] ✓ (verified)
- [[{project}.related-b]] ✓ (verified)

**Metadata initialized:**
- usage: first use recorded
- health: verified
```

### Step 11: Create Project Directory Structure

**When first entity in new project, create all folders:**

```shell
mkdir -p "{graph_path}/entities"
mkdir -p "{graph_path}/concepts"
mkdir -p "{graph_path}/decisions"
mkdir -p "{graph_path}/constraints"
mkdir -p "{graph_path}/processes"
```

**Why:** Graph traversal expects all folders to exist. Prevents errors in subsequent operations.

### Step 12: Create Index File

If this is a new project initialization (first entity in project):

Follow the workflow in [../templates/index-node.md](../templates/index-node.md):

1. Check if `{project}.index.md` exists: `Read("{graph_path}/{project}.index.md")`
2. If not exists, create from template with:
   - Quick stats (entity counts by type)
   - Architecture diagram (simplified Mermaid)
   - Browse by category links
   - Quick links organized by role
   - Search by concern table
3. If exists, prompt: "{project}.index.md already exists. [Skip] [Update]"

**Note:** Index file provides human-readable landing page for the knowledge graph.

### Step 13: Create Obsidian Bases Dashboard

**Default behavior:** Create bases dashboard. Warn and continue if creation fails.

1. Check if `{project}.graph.base` already exists: `Read("{graph_path}/{project}.graph.base")`
   - If exists: Skip to Step 15
   - If not exists: Proceed to create
2. Create using `../bases/ops/ADD.md` → `../bases/templates/graph-base.yaml`
3. On any failure (template missing, validation error):
   - Log warning: "Bases dashboard creation failed: {reason}. Continuing without."
   - Continue to Step 14

**Note:** This step is a soft default—creation failures are tolerated.

### Step 14: Validate {project}.graph.base

**Requires:** `obsidian cli command`

After creating/updating `{project}.graph.base`, validate it:

```shell
obsidian base:views path="{memory}/{project}/{project}.graph.base"
```

**Validation checks:**

- YAML structure valid
- All views parse correctly
- Filters syntax valid
- Formulas compile successfully

**If validation fails:**

1. **Warn:** "{project}.graph.base validation failed: {details}. Continuing with unvalidated file."
2. **Continue operation** — do not block on validation errors

### Step 15: Create Mermaid Diagrams

**Default behavior:** Create Mermaid diagrams. Warn and continue if creation fails.

1. Check if diagram files already exist:
   - `Read("{graph_path}/{project}.graph-sequence.md")`
   - `Read("{graph_path}/{project}.graph-relationships.md")`
   - If both exist: Skip this step to preserve human customizations
2. Try to create using `../mermaid/ops/ADD.md` → `../templates/*.md` if available
3. On any failure (template missing, syntax error):
   - Log warning: "Mermaid diagram creation failed: {reason}. Continuing without."
   - Continue to report results

**Note:** This step is a soft default—creation failures are tolerated. The feature can be disabled by deleting the `.md` files and ignoring warnings.

## Best Practices

- Always confirm before writing
- Check for existing entity before creating
- Offer UPDATE when entity exists
- Infer triggers from file paths (module structure)
- Keep descriptions concise (2-3 sentences)
- Extract constraints from code comments/docstrings
- Validate bidirectional refs before reporting success
- Warn if related entities not found, but proceed with ADD
- **Recommended: Create available artifacts on project initialization:**
  - `{project}.index.md` - Landing page
  - `{project}.graph.base` - Obsidian Bases dashboard
  - `{project}.graph-sequence.md` - Mermaid diagrams
  - `{project}.graph-relationships.md` - Mermaid diagrams

## Quick Reference

| Artifact                           | Location                       | Purpose                  | Created When |
| ---------------------------------- | ------------------------------ | ------------------------ | ------------ |
| `{project}.index.md`               | `{memory}/{project}/`          | Landing page             | First entity |
| `{project}.graph.base`             | `{memory}/{project}/`          | Obsidian Bases dashboard | First entity |
| `{project}.graph-sequence.md`      | `{memory}/{project}/`          | Mermaid diagrams         | First entity |
| `{project}.graph-relationships.md` | `{memory}/{project}/`          | Mermaid diagrams         | First entity |
| Entity nodes                       | `{memory}/{project}/entities/` | Knowledge nodes          | Each entity  |

## Optional Skill Dependencies

Use these skills when available:

| Skill                | Purpose                                              |
| -------------------- | ---------------------------------------------------- |
| `obsidian-markdown`  | Proper Obsidian-flavored Markdown syntax in entities |
| `obsidian-bases`     | Extended dashboard features and validation           |

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
