# DELETE Operation — Remove Entity from Knowledge Graph

## When to Use This Operation

- User says "delete entity X", "remove entity X"
- User selects "DELETE" from stale entity warning
- Entity flagged with `needs_delete = true`
- User explicitly requests deletion

## When NOT to Use This Operation

- User wants to create new entity (use ADD operation)
- User wants to update existing entity (use UPDATE operation)
- User wants to query/load context (use QUERY operation)
- Deletion not confirmed by user

## Critical Rules

**RULE 1 — CONFIRMATION REQUIRED**
> Never delete an entity without user confirmation. Always prompt and wait for explicit confirmation.

**RULE 2 — BIDIRECTIONAL REFERENCE CLEANUP**
> Always clean bidirectional references from all related entities before deleting.

**RULE 3 — ORPHAN DETECTION**
> Warn if deletion causes related entities to become orphaned (no remaining relations).

## Workflow

### Step 1: Resolve Paths

Resolve `{vault}` and `{project}`:

1. Check user message for explicit paths
2. Auto-discover vault path (common locations: `~/Documents/Obsidian Vault`, `~/Obsidian`, `%USERPROFILE%/Documents/Obsidian Vault`, check environment variable `OBSIDIAN_VAULT`)
3. Extract project name from `{cwd}` basename or git repo
4. If ambiguous, ask user

Set `{graph_path}` = `{vault}/Memory/{project}/`

### Step 2: Read Entity

Load the entity file to extract metadata and `related` field:

```
Read("{graph_path}/entities/{entity-name}.md")
```

Extract the `related` field to identify bidirectional references that need cleanup.

If entity file cannot be read (corrupted, missing permissions):

- Report error: "Cannot read entity file" + error details
- Abort operation

### Step 3: Show Confirmation

Show confirmation dialog with actual related entities:

```markdown
### Delete Entity: {entity-name}

**Warning:** This action cannot be undone.

Entity will be removed along with:
- Bidirectional reference from [[{related-1}]]
- Bidirectional reference from [[{related-2}]]

[Confirm] [Cancel]
```

Wait for user confirmation. If user cancels, abort without changes.

### Step 4: Clean Bidirectional References

**⚠️ ATOMICITY REQUIREMENT:**

Bidirectional ref cleanup and file deletion should be atomic.
If file deletion fails after refs are cleaned, entity file exists but has no relations (orphaned).

**Recommended approach:**

1. Mark entity: Set `health.pending_deletion = true` before cleaning refs
2. Clean refs: Remove bidirectional references (safe to retry)
3. Delete file: Only after refs cleaned
4. On file delete failure: Entity orphaned — refs gone, file remains

**Note:** DELETE cannot be fully rolled back once refs are cleaned.

For each related entity:

1. Load the related entity: `Read("{graph_path}/entities/{related}.md")`
2. Remove `[[{entity-name}]]` from `related` field
3. Check if related entity becomes orphaned (no remaining relations)
4. Write updated related entity
5. If orphaned, add to orphaned list for reporting

### Step 5: Delete Entity File

```bash
rm "{graph_path}/entities/{entity-name}.md"
```

If file not found, warn but report references cleaned.

**Error handling:** If `rm` fails (permissions, file locked, read-only):

- Report: "Cannot delete entity file: {error}"
- Check file permissions and ownership
- Offer: "Retry as admin / Skip file deletion / Abort"
- If skipped: Entity remains but bidirectional refs are cleaned
- Note in report: "File deletion failed, manual removal required"

### Step 6: Report Deletion

```markdown
### DELETE Complete

**Deleted:** {entity-name}
**File removed:** `{graph_path}/entities/{entity-name}.md`

**References cleaned:**
- [[related-a]] — reference removed
- [[related-b]] — reference removed

**Orphaned entities:** None
```

If orphaned entities exist:

```markdown
**Orphaned entities:**
- [[only-related]] — no remaining relations
```

## Health Check Integration

Use [lifecycle-management.md](../helpers/lifecycle-management.md) for health operations.

### During DELETE

Before deletion, verify entity is not critical to other operations:

```python
if entity.importance == "critical":
    warn("Entity marked as critical. Confirm deletion.")
```

## Best Practices

- Never delete without confirmation
- Always collect related entities before deletion
- Clean bidirectional refs from ALL related entities
- Warn about orphaned entities in report
- Provide clear rollback instructions if deletion was accidental (restore from git)
- Consider offering "archive" option instead of delete for important entities

### Step 7: Propagate Deletion to Visualizations

Trigger regeneration of visualization artifacts to remove deleted entity:

#### Mermaid Diagrams

1. Check if `graph-sequence.md` or `graph-relationships.md` exists: `Read("{graph_path}/graph-*.md")`
2. If exists, remove any interactions involving deleted entity
3. Update diagram to reflect removal
4. Regenerate diagrams with remaining entities

**If regeneration fails:**

- Log: "Mermaid diagram update failed: {error}"
- Report: "⚠️ Manual diagram update may be needed"
- Continue without failing the DELETE operation

#### Obsidian Bases Dashboard

1. Check if `graph.base` exists: `Read("{graph_path}/graph.base")`
2. Bases will automatically reflect deletion (file-based)
3. No manual update needed for Bases

**Note:** The base dashboard updates automatically on file deletion.

#### Index File

1. Check if `index.md` exists: `Read("{graph_path}/index.md")`
2. If mentions deleted entity, mark as stale or remove reference
3. Log: "Updated index.md references"

### Step 8: Final Report

```markdown
### DELETE Complete

**Deleted:** {entity-name}
**File removed:** `{graph_path}/entities/{entity-name}.md`

**References cleaned:**
- [[related-a]] — reference removed
- [[related-b]] — reference removed

**Orphaned entities:** None

**Visualizations updated:**
- ✓ graph-relationship.md — entity removed from diagrams
- ✓ graph-sequence.md — entity removed from diagrams
- ✓ graph.base — automatically updated
- ✓ index.md — references updated (if applicable)

**Rollback:** If deletion was accidental, restore from git: `git checkout {file-path}`
```

---

## See Also

**Related Operations:**

- [ADD](./ADD.md) — Create new entities
- [UPDATE](./UPDATE.md) — Modify existing entities
- [RENAME](./RENAME.md) — Rename/move entities
- [QUERY](./QUERY.md) — Load entity context

**Related Assets:**

- [lifecycle-management.md](../helpers/lifecycle-management.md) — Manage entity lifecycle
- [graph-traversal.md](../helpers/graph-traversal.md) — Traverse related entities
