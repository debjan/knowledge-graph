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

### Step 0: Resolve Paths

Resolve `{vault}` and `{project}`:

1. Check user message for explicit paths
2. Auto-discover vault path (common locations)
3. Extract project name from `{cwd}` basename or git repo
4. If ambiguous, ask user

Set `{graph_path}` = `{vault}/Memory/{project}/`

### Step D1: Show Confirmation

```markdown
### Delete Entity: {entity-name}

**Warning:** This action cannot be undone.

Entity will be removed along with:
- Bidirectional reference from [[{related-1}]]
- Bidirectional reference from [[{related-2}]]

[Confirm] [Cancel]
```

Wait for user confirmation. If user cancels, abort without changes.

### Step D2: Collect Related Entities

Load entity to get `related` field:

```
Read("{graph_path}/entities/{entity-name}.md")
```

Extract all wiki-links from `related` field.

If entity has no related entities, proceed directly to file removal.

### Step D3: Clean Bidirectional References

For each related entity:

1. Load the related entity: `Read("{graph_path}/entities/{related}.md")`
2. Remove `[[{entity-name}]]` from `related` field
3. Check if related entity becomes orphaned (no remaining relations)
4. Write updated related entity
5. If orphaned, add to orphaned list for reporting

### Step D4: Delete Entity File

```bash
rm "{graph_path}/entities/{entity-name}.md"
```

If file not found, warn but report references cleaned.

### Step D5: Report Deletion

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
