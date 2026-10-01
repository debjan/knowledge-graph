# DELETE Operation - Remove Entity from Knowledge Graph

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

### RULE 1: CONFIRMATION REQUIRED

> Never delete an entity without user confirmation. Always prompt and wait for explicit confirmation.

### RULE 2: BIDIRECTIONAL REFERENCE CLEANUP

> Always clean bidirectional references from all related entities before deleting.

### RULE 3: ORPHAN DETECTION

> Warn if deletion causes related entities to become orphaned (no remaining relations).

### RULE 4: VALIDATED PATH ONLY

> Delete exactly one validated, resolved file path. Never delete a directory, a glob, or a path that escaped `{graph_path}`.
> Enforce [safe-paths.md](../helpers/safe-paths.md) before any shell command.

## Workflow

### Step 1: Resolve and Validate Paths

Resolve `{vault}`, `{memory}` and `{project}`:

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

Set `{graph_path}` = `{vault}/{memory}/{project}/`

Validate identifiers before using them in any path (enforce [safe-paths.md](../helpers/safe-paths.md)):

1. `{project}` and `{entity-name}` match `^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$`
2. `{entity-name}` is a single path component - no `/`, `\`, `..`, quotes, `$`, backticks, whitespace, or leading `-`
3. Build the target as `{graph_path}/entities/{project}.{entity-name}.md`, resolve it, and assert it is still inside `{graph_path}/entities/`
4. Refuse directories, symlinks resolving outside `{graph_path}`, and non-`.md` targets

If validation fails:

- Report: "Invalid entity identifier: {value} - expected kebab-case, e.g. `auth-service`"
- Abort. Do not delete, trim, or escape the value.

### Step 2: Read Entity

Load the entity file to extract metadata and `related` field:

```
Read("{graph_path}/entities/{project}.{entity-name}.md")
```

Extract the `related` field to identify bidirectional references that need cleanup.

If entity file cannot be read (corrupted, missing permissions):

- Report error: "Cannot read entity file" + error details
- Abort operation

### Step 3: Show Confirmation

Show confirmation dialog with actual related entities:

```
### Delete Entity: {project}.{entity-name}

**Warning:** This action cannot be undone.

Entity will be removed along with:
- Bidirectional reference from [[{project}.{related-1}]]
- Bidirectional reference from [[{project}.{related-2}]]

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
4. On file delete failure: Entity orphaned - refs gone, file remains

**Note:** DELETE cannot be fully rolled back once refs are cleaned.

For each related entity:

1. Validate the `{related}` name against the allowlist ([safe-paths.md](../helpers/safe-paths.md)); skip and report any name that fails instead of building a path from it
2. Load the related entity: `Read("{graph_path}/entities/{project}.{related}.md")`
3. Remove `[[{project}.{entity-name}]]` from `related` field
4. Check if related entity becomes orphaned (no remaining relations)
5. Write updated related entity
6. If orphaned, add to orphaned list for reporting

### Step 5: Delete Entity File

Delete exactly one literal, validated path. Do not use globs, `-f`, `-r`, `eval`, or command substitution:

```shell
# {project} and {entity-name} already passed the allowlist in Step 1
rm -- "{graph_path}/entities/{project}.{entity-name}.md"
```

**Windows:** `rm` maps to `Remove-Item`, which has no `--`. Use `-LiteralPath` (no wildcard expansion) and never add `-Recurse`:

```powershell
Remove-Item -LiteralPath "{graph_path}\entities\{project}.{entity-name}.md" -Confirm:$false
```

**Pre-conditions (all must hold):**

- User confirmed in Step 3
- Target resolved inside `{graph_path}/entities/`
- Target is a regular `.md` file, not a directory or external symlink

**Post-condition:** re-check that the path no longer exists and that `{graph_path}/entities/` still exists. If the path still exists, report it - never retry with a broader or recursive delete.

If file not found, warn but report references cleaned.

**Error handling:** If the delete fails (permissions, file locked, read-only):

- Report: "Cannot delete entity file: {error}"
- Check file permissions and ownership
- Offer: "Retry as admin / Skip file deletion / Abort"
- If skipped: Entity remains but bidirectional refs are cleaned
- Note in report: "File deletion failed, manual removal required"

### Step 6: Report Deletion

```
### DELETE Complete

**Deleted:** {project}.{entity-name}
**File removed:** `{graph_path}/entities/{project}.{entity-name}.md`

**References cleaned:**
- [[{project}.related-a]] — reference removed
- [[{project}.related-b]] — reference removed

**Orphaned entities:** None
```

If orphaned entities exist:

```
**Orphaned entities:**
- [[{project}.only-related]] — no remaining relations
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

1. Check if `{project}.graph-sequence.md` or `{project}.graph-relationships.md` exists: `Read("{graph_path}/{project}.graph-*.md")`
2. If exists, remove any interactions involving deleted entity
3. Update diagram to reflect removal
4. Regenerate diagrams with remaining entities

**If regeneration fails:**

- Log: "Mermaid diagram update failed: {error}"
- Report: "⚠️ Manual diagram update may be needed"
- Continue without failing the DELETE operation

#### Obsidian Bases Dashboard

1. Check if `{project}.graph.base` exists: `Read("{graph_path}/{project}.graph.base")`
2. Bases will automatically reflect deletion (file-based)
3. No manual update needed for Bases

**Note:** The base dashboard updates automatically on file deletion.

#### Index File

1. Check if `{project}.index.md` exists: `Read("{graph_path}/{project}.index.md")`
2. If mentions deleted entity, mark as stale or remove reference
3. Log: "Updated {project}.index.md references"

### Step 8: Final Report

```
### DELETE Complete

**Deleted:** {project}.{entity-name}
**File removed:** `{graph_path}/entities/{project}.{entity-name}.md`

**References cleaned:**
- [[{project}.related-a]] — reference removed
- [[{project}.related-b]] — reference removed

**Orphaned entities:** None

**Visualizations updated:**
- ✓ {project}.graph-relationship.md — entity removed from diagrams
- ✓ {project}.graph-sequence.md — entity removed from diagrams
- ✓ {project}.graph.base — automatically updated
- ✓ {project}.index.md — references updated (if applicable)

**Rollback:** If deletion was accidental, restore the validated path from git:

```shell
git checkout -- "{graph_path}/entities/{project}.{entity-name}.md"
```

Never interpolate a raw path into a shell string - see [safe-paths.md](../helpers/safe-paths.md).
```

---

## See Also

**Related Operations:**

- [ADD](./ADD.md) - Create new entities
- [UPDATE](./UPDATE.md) - Modify existing entities
- [RENAME](./RENAME.md) - Rename/move entities
- [QUERY](./QUERY.md) - Load entity context

**Related Assets:**

- [lifecycle-management.md](../helpers/lifecycle-management.md) - Manage entity lifecycle
- [safe-paths.md](../helpers/safe-paths.md) - Validate identifiers and file paths before delete
- [graph-traversal.md](../helpers/graph-traversal.md) - Traverse related entities
