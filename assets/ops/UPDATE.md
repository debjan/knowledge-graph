# UPDATE Operation — Modify Entity in Knowledge Graph

## When to Use This Operation

- User says "update entity X", "refresh entity X"
- User selects "UPDATE" from stale entity warning
- Entity already exists when ADD operation is attempted
- User explicitly requests update

## When NOT to Use This Operation

- User wants to create new entity (use ADD operation)
- User wants to delete entity (use DELETE operation)
- User wants to query/load context (use QUERY operation)
- Entity doesn't exist (use ADD operation)

## Critical Rules

### RULE 1: VALIDATE ENTITY PROPERTIES

> Entity properties must have valid YAML syntax.
> Use `yamllint` for verification if exists, or do manual YAML syntax check (look for missing quotes, incorrect indentation).

### RULE 2: BIDIRECTIONAL REFERENCES

> If updating entity relations, maintain bidirectional links by adding to new relations and removing from old relations.

### RULE 3: CHANGELOG INCREMENT

> Always increment the changelog when updating an entity.

**How to Increment:**

The `changelog` field is an array of version entries. When updating an entity, **append a new entry** rather than modifying existing entries.

**Version Numbering:**

- Simple: Increment patch version (`1.0` → `1.1` or `1.0.0` → `1.0.1`)
- Semantic: Use semantic versioning based on change significance
  - MAJOR: Breaking changes to constraints/patterns
  - MINOR: New patterns, triggers added
  - PATCH: Documentation updates, typo fixes

**New Entry Format:**

```yaml
changelog:
  - version: "1.0"
    date: 2026-04-05
    changes: ["Initial creation"]
  - version: "1.1"  # NEW ENTRY - increment from last
    date: {today}
    changes:
      - "Updated trigger patterns for new file structure"
      - "Added rate limiting constraint"
```

**Field Requirements:**

| Field     | Required | Description                                   |
| --------- | -------- | --------------------------------------------- |
| `version` | Yes      | New version string, incremented from previous |
| `date`    | Yes      | Update date (ISO 8601: YYYY-MM-DD)            |
| `changes` | Yes      | Array of change descriptions (1-5 items)      |

**Best Practices:**

- Keep change descriptions concise (under 100 chars)
- Lead with action verb: "Added", "Fixed", "Updated", "Removed"
- Never modify or delete existing changelog entries - append only

### RULE 4 — HEALTH FLAGS CLEARED

> Clear all health flags after successful UPDATE.

## Workflow

### Step 1: Resolve Paths

Resolve `{vault}` and `{project}`:

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

Set `{graph_path}` = `{vault}/memory/{project}/`

Load `obsidian-markdown` skill

### Step 2: Load Existing Entity

```
Read("{graph_path}/entities/{entity-name}.md")
```

**Error handling:** If entity file cannot be read (corrupted, permissions, I/O error):

- Report: "Cannot read entity file: {error}"
- Check if file is corrupted: attempt backup recovery
- If unrecoverable: Offer to DELETE and re-ADD
- Abort UPDATE operation

### Step 3: Check Health Status

If entity has `needs_update: true` or `needs_delete: true`:

```markdown
Note: Entity "{entity-name}" has pending health issues:
- Stale files: {stale_files}
- Needs update: {needs_update}

Address these during the update? [Yes/No]
```

### Step 4: Extract New Metadata

Re-extract entity metadata from current code state using [entity-extraction.md](../helpers/entity-extraction.md):

1. Parse file content
2. Identify entity type (module, class, function, api-endpoint)
3. Extract name, description, imports
4. Infer category and importance
5. Identify related entities

### Step 5: Show Diff

Present the diff between existing and new:

```markdown
### Entity Update: {entity-name}

**Changes detected:**

#### Frontmatter
- `importance`: high → medium
- `tags`: [+rate-limit] [-legacy-auth]

#### Content
- Description: 2 lines changed
- Agent Context: triggers updated

#### Health
- Stale files: {count} cleared
- needs_update: true → false

[MERGE] [OVERRIDE] [CANCEL]
```

**Options:**

- **MERGE:** Keep both, prefer new values for conflicts, combine tags
- **OVERRIDE:** Replace all with new content (preserve usage statistics only)
- **CANCEL:** Keep existing, abort update

### Step 6: Apply Update

On confirmation:

1. Merge frontmatter (preserve usage; update metadata)
2. Update `updated` to {today}
3. Append changelog entry (increment version per guidance above, add new entry to array)
4. Clear `health.stale_files`
5. Set `health.needs_update = false`
6. Set `health.last_verified = {today}`
7. Write updated entity

**Error handling:** If `Write()` fails (disk full, permissions):

- Report: "Failed to write updated entity: {error}"
- Preserve prepared content in memory for retry
- Offer: "Retry / Save to alternate location / Abort"
- Do not report success if write failed
- Do not clear health flags if write failed

### Step 7: Update Bidirectional References

If related entities changed:

1. For new relations: Add bidirectional links
   - Read `{graph_path}/entities/{new-related}.md`
   - Add `[[{entity-name}]]` to `related` field
   - Write updated related entity

2. For removed relations: Remove bidirectional links
   - Read `{graph_path}/entities/{removed-related}.md`
   - Remove `[[{entity-name}]]` from `related` field
   - Write updated related entity

**Error handling (bidirectional sync failure):**
If updating related entity fails mid-process:

- Log which entities succeeded/failed
- Do not leave refs in inconsistent state
- Rollback completed changes if possible
- Report partial success with list of failed updates
- User must manually fix remaining refs

### Step 8: Report Update

```markdown
### UPDATE Complete

**Entity:** {entity-name}
**Action:** updated
**Version:** {old_version} → {new_version}
**Path:** `{graph_path}/entities/{entity-name}.md`

**Changes:**
- {change_1}
- {change_2}

**Health cleared:** {stale_files_cleared} stale file(s)

**Bidirectional refs:**
- [[new-related]] ✓ (link added)
- [[removed-related]] ✓ (link removed)
```

### Step 9: Sync Dashboard Formulas

If entity template schema changed:

Follow the workflow in [../bases/ops/UPDATE.md](../bases/ops/UPDATE.md):

1. Detect schema changes (new/removed frontmatter fields)
2. Prompt to sync graph.base formulas
3. Regenerate from template if confirmed

## Health Check Integration

Use [lifecycle-management.md](../helpers/lifecycle-management.md) for health operations.

### After UPDATE

Verify implementation files exist:

```python
for file in entity.implementation_files:
    if not file.exists():
        entity.health.stale_files.append(file)
        entity.health.needs_update = True
```

## Best Practices

- Always confirm before updating
- Check health status and offer to address issues
- Offer MERGE and OVERRIDE options
- Preserve usage statistics on OVERRIDE
- Validate bidirectional refs before reporting success
- Clear health flags on successful update
- Increment version for tracking changes
- Offer to sync dashboard formulas when schema changes

Read [bases](../bases/ops/UPDATE.md)
Read [mermaid](../mermaid/ops/UPDATE.md)

---

## See Also

**Related Operations:**

- [ADD](./ADD.md) — Create new entities
- [DELETE](./DELETE.md) — Remove entities
- [RENAME](./RENAME.md) — Rename/move entities
- [QUERY](./QUERY.md) — Load entity context

**Related Assets:**

- [entity-extraction.md](../helpers/entity-extraction.md) — Extract entity metadata
- [lifecycle-management.md](../helpers/lifecycle-management.md) — Manage entity lifecycle
