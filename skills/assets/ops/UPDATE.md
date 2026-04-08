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

**RULE 1 — USER CONFIRMATION REQUIRED**
> Always present entity diff to the user before updating. Never write without confirmation.

**RULE 2 — BIDIRECTIONAL REFERENCES**
> If updating entity relations, maintain bidirectional links by adding to new relations and removing from old relations.

**RULE 3 — CHANGELOG INCREMENT**
> Always increment the changelog when updating an entity.

**RULE 4 — HEALTH FLAGS CLEARED**
> Clear all health flags after successful UPDATE.

## Workflow

### Step 0: Resolve Paths

Resolve `{vault}` and `{project}`:

1. Check user message for explicit paths
2. Auto-discover vault path (common locations)
3. Extract project name from `{cwd}` basename or git repo
4. If ambiguous, ask user

Set `{graph_path}` = `{vault}/Memory/{project}/`

### Step U1: Load Existing Entity

```
Read("{graph_path}/entities/{entity-name}.md")
```

### Step U2: Check Health Status

If entity has `needs_update: true` or `needs_delete: true`:

```markdown
Note: Entity "{entity-name}" has pending health issues:
- Stale files: {stale_files}
- Needs update: {needs_update}

Address these during the update? [Yes/No]
```

### Step U3: Extract New Metadata

Re-extract entity metadata from current code state using [entity-extraction.md](../helpers/entity-extraction.md):

1. Parse file content
2. Identify entity type (module, class, function, api-endpoint)
3. Extract name, description, imports
4. Infer category and importance
5. Identify related entities

### Step U4: Show Diff

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

### Step U5: Apply Update

On confirmation:

1. Merge frontmatter (preserve usage; update metadata)
2. Update `updated` to today
3. Increment changelog version
4. Clear `health.stale_files`
5. Set `health.needs_update = false`
6. Set `health.last_verified = today`
7. Write updated entity

### Step U6: Update Bidirectional References

If related entities changed:

1. For new relations: Add bidirectional links
   - Read `{graph_path}/entities/{new-related}.md`
   - Add `[[{entity-name}]]` to `related` field
   - Write updated related entity

2. For removed relations: Remove bidirectional links
   - Read `{graph_path}/entities/{removed-related}.md`
   - Remove `[[{entity-name}]]` from `related` field
   - Write updated related entity

### Step U7: Report Update

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

### Step U8: Sync Dashboard Formulas

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
