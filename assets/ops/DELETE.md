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

**Order matters.** Clean references *before* deleting the file: while the entity still exists, every referrer's link still resolves, and a failure at this stage is recoverable. Deleting first leaves dangling links in every referrer until cleanup succeeds.

1. **Collect** the referrers whose `related` lists contain `[[{project}.{entity-name}]]`. Read each one and record its current list; do not write yet.
2. **Apply** the removals. Each write is independent and idempotent, so a retry is safe.
3. **On failure:** stop before touching the entity file. Report which referrers were cleaned and which were not. The entity and its file are untouched, so the graph is still consistent - the user can retry.

If the collect phase finds zero referrers, say so and continue: a node with no inbound links is a legitimate delete.

For each related entity:

1. Validate the `{related}` name against the allowlist ([safe-paths.md](../helpers/safe-paths.md)); skip and report any name that fails instead of building a path from it
2. Load the related entity: `Read("{graph_path}/entities/{project}.{related}.md")`
3. Remove `[[{project}.{entity-name}]]` from `related` field
4. Check if related entity becomes orphaned (no remaining relations)
5. Write updated related entity
6. If orphaned, add to orphaned list for reporting

**Do not set any flag on the entity before deleting it.** An earlier draft of this workflow proposed `health.pending_deletion = true`, but that field is not in the node schema: VERIFY CHECK 5 ignores it, the templates do not contain it, and it would be deleted moments later anyway. If the delete fails and you need a breadcrumb, report it - do not invent frontmatter.

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
- Step 4 completed without unreported failures
- Target resolved inside `{graph_path}/entities/`
- Target is a regular `.md` file, not a directory or external symlink

**Post-condition:** re-check that the path no longer exists and that `{graph_path}/entities/` still exists. If the path still exists, report it - never retry with a broader or recursive delete.

If file not found, warn but report references cleaned.

**Error handling:** If the delete fails (permissions, file locked, read-only):

- Report: "Cannot delete entity file: {error}"
- Check file permissions and ownership
- Offer: "Retry / Skip file deletion / Abort"
- If skipped: the entity file remains, but its references are already cleaned - tell the user the node is now orphaned and needs UPDATE (re-add links) or another DELETE attempt
- Never report `DELETE Complete` when the file is still present

### Step 6: Propagate Deletion to Visualizations

Regenerate the visualization artifacts after the file is gone:

#### Mermaid Diagrams

1. Check if `{project}.graph-sequence.md` or `{project}.graph-relationships.md` exists: `Read("{graph_path}/{project}.graph-*.md")`
2. If exists, remove any interactions involving the deleted entity
3. Regenerate diagrams with the remaining entities

**If regeneration fails:** log "Mermaid diagram update failed: {error}", warn that manual update may be needed, and continue - a diagram is not a reason to fail a delete.

#### Obsidian Bases Dashboard

`{project}.graph.base` is file-based and reflects the deletion automatically. No rewrite needed; do not touch it.

#### Index File

1. Check if `{project}.index.md` exists: `Read("{graph_path}/{project}.index.md")`
2. Remove or mark stale any reference to the deleted entity
3. Update the entity counts

### Step 7: Final Report

This is the **only** report. Do not also emit an interim report before the visualization step.

```
### DELETE Complete

**Deleted:** {project}.{entity-name}
**File removed:** `{graph_path}/entities/{project}.{entity-name}.md`

**References cleaned:**
- [[{project}.related-a]] — reference removed
- [[{project}.related-b]] — reference removed

**Orphaned entities:** None

**Visualizations updated:**
- ✓ {project}.graph-relationships.md — entity removed
- ✓ {project}.graph-sequence.md — entity removed
- ✓ {project}.graph.base — automatic (file-based)
- ✓ {project}.index.md — references and counts updated

**Rollback:** if this was a mistake, restore the file from version control, then re-add the inbound links.
```

Only mention rollback if the graph directory is actually under version control. Check before promising it:

```shell
git -C "{graph_path}" rev-parse --is-inside-work-tree 2>/dev/null && echo "versioned" || echo "not versioned"
```

If it is versioned, the restore command takes the same literal path validated in Step 1:

```shell
git -C "{vault}" checkout -- "{memory}/{project}/entities/{project}.{entity-name}.md"
```

If it is not versioned, say so plainly: "Not under version control - restore from your backup." Never present `git checkout` as a recovery path that does not exist.

---

## Health Check Integration

Use [lifecycle-management.md](../helpers/lifecycle-management.md) for health operations.

### During DELETE

Before deletion, check whether the entity is load-bearing:

```python
if entity.importance == "high" and len(inbound_refs) > 3:
    warn("Entity is high-importance and referenced by %d nodes. Confirm deletion." % len(inbound_refs))
```

Suggest the alternative explicitly: "Archive instead of delete? Set `status: deprecated` and keep the node." For an entity a human still browses, that is usually the better outcome.

## Best Practices

- Never delete without confirmation
- Clean references before deleting the file, never after
- Warn about orphaned entities in the report
- Offer `status: deprecated` before deletion for high-importance nodes
- Do not promise a git rollback unless the graph is a git working tree
- Never set frontmatter fields that are not in the schema (`pending_deletion` and friends)

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
