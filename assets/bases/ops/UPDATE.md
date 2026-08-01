# Base UPDATE Operation

Sync {project}.graph.base formulas with entity template schema changes.

## Trigger

- Entity template schema changes detected
- Explicit "sync base" or "update base formulas" command
- User accepts offer to regenerate after schema changes

## When to Sync

Schema sync is needed when:

- Entity template frontmatter fields are added/removed
- Field types change (affecting formula logic)
- New health or usage metadata fields introduced

## Workflow

### Step 1: Load `obsidian-bases` skill

### Step 2: Detect Schema Change

Resolve `{vault}`, `{memory}` and `{project}`.

If ambiguous, enforce [Critical Rule 1](../../../SKILL.md#rule-1-resolve-paths-once)

Set `{graph_path}` = `{vault}/{memory}/{project}/`

Compare entity template frontmatter fields with {project}.graph.base formulas:

1. Read [entity template](../../templates/entity-node.md)
2. Extract frontmatter fields (type, category, importance, status, usage, health, etc.)
3. Read {project}.graph.base: `{graph_path}/{project}.graph.base`
4. Extract formulas from {project}.graph.base
5. Check if formulas reference all relevant frontmatter fields

### Step 3: Prompt for Sync

If schema mismatch detected:

```
Entity schema has changed. {project}.graph.base formulas may be outdated.

**Missing formulas:**
- {field_1} (new frontmatter field)
- {field_2} (new frontmatter field)

**Orphaned formulas:**
- {formula_1} (references removed field)

Update {project}.graph.base to match current schema?

[Yes] — Regenerate formulas from template
[No] — Keep existing
[Show diff] — Preview changes
```

### Step 4: Apply Sync

On confirmation:

1. Load `obsidian-bases` skill
2. Read [graph-base template](../templates/graph-base.yaml)
3. Write to: `{graph_path}/{project}.graph.base`
4. Report: "{project}.graph.base updated with {count} formulas"

### Step 5: Report Results

```
✓ Synced {project}.graph.base formulas with entity schema
  - Added: {added_count} formulas
  - Removed: {removed_count} formulas
```

## Manual Sync Request

User can request sync explicitly:

> Update the graph base

Response: Execute Step 1 through 4, skipping the conditional check in Step 2.

## Preserving Human Customization

If human has modified {project}.graph.base:

1. Detect human modifications (Step 2)
2. Prompt before overwrite (Step 3)
3. If user declines, keep existing

Custom base files (not `{project}.graph.base`) are never touched by schema sync.
