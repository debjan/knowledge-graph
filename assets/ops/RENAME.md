# RENAME Operation - Rename Entity in Knowledge Graph

Rename an entity while preserving its history, usage metadata, and relationships.

## When to Use This Operation

- User says "rename entity X to Y", "move entity X" (conceptual rename)
- File or module has been renamed in the codebase
- Entity name is no longer accurate or needs clarification
- Consolidating duplicate or overlapping entities

## When NOT to Use This Operation

- User wants to create a new entity (use ADD operation)
- User wants to update entity content without changing its identity (use UPDATE operation)
- User wants to delete and start fresh (use DELETE then ADD - loses history intentionally)
- Entity doesn't exist (entity must exist to be renamed)

## Critical Rules

### RULE 1: HISTORY PRESERVATION

> The RENAME operation MUST preserve all usage statistics, changelog, and health metadata. Do not reset these values.

### RULE 2: BIDIRECTIONAL REFERENCE UPDATE

> All entities that reference the old name MUST be updated to reference the new name.

### RULE 3: TOMBSTONE REDIRECT

> Leave a tombstone at the old path that redirects to the new entity for backward compatibility.

### RULE 4: ATOMIC OPERATION

> Either complete all steps successfully, or rollback to original state. Do not leave the graph in an inconsistent state.

## Workflow

### Step 1: Resolve and Validate Paths

Resolve `{vault}`, `{memory}` and `{project}`:

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

Set `{graph_path}` = `{vault}/{memory}/{project}/`

Validate both names before they reach a path (enforce [safe-paths.md](../helpers/safe-paths.md)):

1. `{project}`, `{old-name}` and `{new-name}` match `^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$`
2. Each name is a single path component - no `/`, `\`, `..`, quotes, `$`, backticks, whitespace, or leading `-`
3. Every resolved path stays inside `{graph_path}/entities/` and ends in `.md`

If a name fails validation, report the offending value and abort. Never escape or trim it into something valid.

### Step 2: Load Existing Entity

```
Read("{graph_path}/entities/{project}.{old-name}.md")
```

**Error handling:** If entity file cannot be read (corrupted, permissions, I/O error):

- Report: "Cannot read entity file: {error}"
- Check if file is corrupted: attempt backup recovery
- If unrecoverable: Offer to DELETE and re-ADD (loses history)
- Abort RENAME operation

Validate entity is healthy enough to rename:

- If entity has `needs_delete: true`, warn: "Entity flagged for deletion. Proceed?"
- If entity is stale, proceed but note: "Entity is stale; consider UPDATE first"

### Step 3: Check Target Name Availability

Check if target name already exists:

```
Read("{graph_path}/entities/{project}.{new-name}.md")
```

If target exists:

- **If target is the same entity:** Error: "Cannot rename entity to itself"
- **If target is different entity:** Error: "Target name already exists. Choose different name or merge entities"
- **If target file unreadable:** Warn and ask: "Target file exists but cannot be read. Replace? [Yes/No]"

### Step 4: Extract and Prepare

Extract from old entity:

- All frontmatter fields (preserve exactly)
- Full document content
- Usage statistics (`usage.last_used`, `usage.use_count` - do NOT reset)
- Changelog (preserve full history)
- Health flags (note current state, clear after successful rename)
- Bidirectional references (`related` field - list of entities pointing to old name)

Prepare new entity document with:

- Same content as old entity
- `name` updated to `{project}.{new-name}`
- `updated` set to {today}
- Changelog entry added: "Renamed from {project}.{old-name} on {today}"
- Keep all `usage.*` fields unchanged
- Keep all `health.*` fields (will be cleared after successful rename)

### Step 5: Write New Entity

Write the new entity **before** touching references or the old file. Every later step depends on the new path existing, so this is the ordering that keeps the graph resolvable at every point.

The `entities/` folder already exists (the old entity lives in it), so no directory work is needed:

```
Write("{graph_path}/entities/{project}.{new-name}.md", {prepared_content})
```

**Error handling:** If `Write()` fails:

- Report: "Failed to create new entity file: {error}"
- DO NOT delete or modify the old entity - preserve original
- Abort operation before any reference or tombstone change
- Nothing changed on disk except the failed write; retry after fixing the filesystem issue

**Post-condition:** `{graph_path}/entities/{project}.{new-name}.md` exists and the old file is untouched. Do not continue until this holds.

### Step 6: Update Bidirectional References

Collect all entities that reference `{project}.{old-name}`.

The search pattern is built from a validated name and escaped, so a crafted name cannot widen or break the match:

```python
import re

# {old-name} validated per Step 1 (allowlist, single component)
pattern = re.escape(f"[[{{project}}.{old_name}]]")
matches = Grep(pattern=pattern, path="{graph_path}/entities", type="md")
```

If the Grep tool supports fixed-string search, prefer it over a regex (`fixed_strings: true` / literal mode) - no escaping needed.

Never pass `{old-name}` into a regex or shell pattern raw: an unescaped `.` matches any character, and `*`, `[`, `(` or `\` change the pattern or fail outright.

**Two-phase update (recommended):**

1. **Collect:** read every referrer, record its current `related` list, and build the edited content. Do not write yet.
2. **Apply:** if all referrers were read successfully, write them all. The new entity from Step 5 already exists, so an updated link always resolves.

For each referencing entity:

1. Load the entity: `Read("{graph_path}/entities/{project}.{referrer}.md")`
2. Replace `[[{project}.{old-name}]]` with `[[{project}.{new-name}]]` in `related` field
3. Update timestamp: mention "Updated references: {project}.{old-name} → {project}.{new-name}"
4. Write updated entity

**Error handling:** If a referencing entity cannot be updated:

- Roll back the referrer edits already applied, using the `related` lists recorded in the collect phase
- If rollback succeeds: remove the new entity file created in Step 5 (the only file this operation created) and abort, leaving the graph exactly as it was
- If rollback fails: keep the new entity, do **not** create the tombstone (the old name must keep resolving), and report partial success with the list of failed referrers
- Never leave a referrer pointing at `{project}.{new-name}` when that file does not exist

### Step 7: Replace Old Entity with Tombstone

The old path is **overwritten** with tombstone content - it is not written and then deleted. A separate write-then-delete pair can fail between the two steps and destroy both the old node and the redirect; a single overwrite cannot.

Writing to the old path overwrites an existing file, so the explicit user confirmation from the rename request is required here (RULE 9). Present it as:

```
Replace {project}.{old-name}.md with a redirect tombstone?
- New entity: {graph_path}/entities/{project}.{new-name}.md (written)
- Old path keeps a tombstone pointing at the new entity
[Replace with tombstone] [Keep old file unchanged]
```

Tombstone content:

```
---
name: {project}.{old-name}
type: tombstone
redirect_to: "[[{project}.{new-name}]]"
created: {today}
---

# Entity Moved

**{project}.{old-name}** has been renamed to **[[{project}.{new-name}]]**.

See: [[{project}.{new-name}]] for current entity information.

---

*This file is automatically generated by RENAME operation.*
*Remove this file after 30 days or when all references are updated.*
```

**Error handling:** If the tombstone write fails:

- Warn: "Could not write tombstone at {old-path}"
- The old entity keeps its original content (a failed overwrite leaves the file intact), so the old name still resolves to valid content
- Note in report: "Old entity kept unchanged; manual tombstone creation may be needed"
- Continue operation - this is a degraded but consistent state

**Post-condition:** `{graph_path}/entities/{project}.{new-name}.md` exists and `{graph_path}/entities/{project}.{old-name}.md` contains the tombstone with `redirect_to`. Never run a delete, `rm`, or glob to "finish" the rename; overwriting is the whole operation.

### Step 8: Clear Health Flags

Mark rename as complete in new entity:

1. Set `health.last_verified = {today}`
2. Set `health.needs_update = false`
3. Set `health.needs_delete = false`
4. Set `health.stale_files = []`

**Note:** Preserve `usage.*` fields - do not modify.

### Step 9: Propagate Rename to Visualizations

Update visualization artifacts:

#### Mermaid Diagrams

1. Check if `{project}.graph-sequence.md` or `{project}.graph-relationships.md` exists: `Read("{graph_path}/{project}.graph-*.md")`
2. Regenerate: Replace `{project}.{old-name}` with `{project}.{new-name}` in diagram
3. Update diagrams where entity participates
4. Include note: "Entity renamed: {project}.{old-name} → {project}.{new-name}"

#### Obsidian Bases Dashboard

1. `{project}.graph.base` will auto-reflect (file-based)
2. No manual update needed for Bases

#### Index File

1. Update entity counts
2. Update any direct references to old name

### Step 10: Report RENAME

```
### RENAME Complete

**Entity:** {project}.{old-name} → {project}.{new-name}

**History preserved:**
- Usage count: {use_count}
- Last used: {last_used}
- Changelog entries: {changelog_count}

**New path:** `{graph_path}/entities/{project}.{new-name}.md`
**Old path (tombstone):** `{graph_path}/entities/{project}.{old-name}.md`

**Bidirectional references updated:**
- [[{project}.referrer-a]] → Updated ✓
- [[{project}.referrer-b]] → Updated ✓

**Visualizations:**
- ✓ {project}.graph-sequence.md — entity renamed in diagrams
- ✓ {project}.graph.base — automatically updated
- ✓ {project}.index.md — references updated

**Tombstone:** Created at old path (redirects to new entity)
```

If partial success:

```
### RENAME Complete (Partial)

**Entity:** {project}.{old-name} → {project}.{new-name} ✓ Created

**Warnings:**
- Bidirectional refs incomplete: [[{project}.failed-referrer]] could not be updated
- Tombstone not created: manual redirect needed

**Action required:**
1. Check file permissions in {graph_path}/entities/
2. Manually update [[{project}.failed-referrer]] to reference [[{project}.{new-name}]]
3. Consider creating tombstone at {old-path}
```

## Health Check Integration

Use [lifecycle-management.md](../helpers/lifecycle-management.md) to update entity lifecycle.

### After RENAME

Verify references are correctly updated:

```python
new_entity = Read("{graph_path}/entities/{project}.{new-name}.md")
for ref in new_entity.related:
    ref_entity = Read("{graph_path}/entities/{project}.{ref}.md")
    if "{project}.{new-name}" not in ref_entity.related:
        warn(f"Bidirectional ref broken: {ref} doesn't reference {project}.{new-name}")
        ref_entity.related.append("{project}.{new-name}")
        Write(ref_entity)
```

The tombstone needs no extra metadata: it is a `type: tombstone` node with `redirect_to`, and the audit trail lives in the renamed entity's changelog. Do not invent a cleanup field such as `health.auto_delete_after` - it is not in the node schema and VERIFY CHECK 5 would flag it. Record the intended removal date in the report instead:

```
Tombstone removal: review {project}.{old-name} after 30 days or when no references remain.
```

## Best Practices

- Always confirm before renaming - user must explicitly approve
- **RESERVED:** Never rename core system entities (ADD, UPDATE, DELETE, QUERY, RENAME) - could break operation detection
- Rename early in project lifecycle to minimize broken references
- Use tombstone redirects for graceful migration over time
- After rename, do a quick grep to find any remaining hardcoded references
- Consider keeping tombstones for at least 30 days or until all external references updated
- When to use RENAME vs DELETE+ADD:
  - **Use RENAME:** Same entity, different name; preserve history
  - **Use DELETE+ADD:** Fundamentally different entity; intentional history reset
- Update any external documentation or README files referencing old name

## Change Detection Integration

Update [change-detection.md](../helpers/change-detection.md) to detect renames:

```python
# File rename detection
if old_file.exists() and not new_file.exists() and content_similarity > 0.8:
    trigger "RENAME operation"  # Instead of DELETE+ADD
```

### Rename Confidence Levels

| Confidence | Trigger                          | Action                      |
| ---------- | -------------------------------- | --------------------------- |
| **High**   | File renamed, same content       | Suggest RENAME operation    |
| **Medium** | File renamed, minor changes      | Suggest UPDATE after rename |
| **Low**    | File not found, new file present | Treat as DELETE+ADD         |

---

## See Also

**Related Operations:**

- [ADD](./ADD.md) - Create new entities
- [UPDATE](./UPDATE.md) - Modify existing entities
- [DELETE](./DELETE.md) - Remove entities
- [QUERY](./QUERY.md) - Load entity context

**Related Assets:**

- [change-detection.md](../helpers/change-detection.md) - Detect file renames
- [safe-paths.md](../helpers/safe-paths.md) - Validate old and new names before any file operation
- [lifecycle-management.md](../helpers/lifecycle-management.md) - Manage entity lifecycle
