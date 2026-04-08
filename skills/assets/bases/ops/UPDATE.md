# Base UPDATE Operation

Sync graph.base formulas with entity template schema changes.

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

### Step 1: Detect Schema Change

Compare entity template frontmatter fields with graph.base formulas:

1. Read [entity template](../../templates/entity-node.md)
2. Extract frontmatter fields (type, category, importance, status, usage, health, etc.)
3. Read graph.base: `{graph_path}/graph.base`
4. Extract formulas from graph.base
5. Check if formulas reference all relevant frontmatter fields

### Step 2: Prompt for Sync

If schema mismatch detected:

```
Entity schema has changed. graph.base formulas may be outdated.

**Missing formulas:**
- {field_1} (new frontmatter field)
- {field_2} (new frontmatter field)

**Orphaned formulas:**
- {formula_1} (references removed field)

Update graph.base to match current schema?

[Yes] — Regenerate formulas from template
[No] — Keep existing
[Show diff] — Preview changes
```

### Step 3: Apply Sync

On confirmation:

1. Read [graph-base template](../templates/graph-base.yaml)
2. Write to: `{graph_path}/graph.base`
3. Report: "graph.base updated with {count} formulas"

### Step 4: Report Results

```
✓ Synced graph.base formulas with entity schema
  - Added: {added_count} formulas
  - Removed: {removed_count} formulas
```

## Manual Sync Request

User can request sync explicitly:

> Update the graph base

Response: Execute Step 1 through 3 without detecting changes first.

## Preserving Human Customizations

If human has modified graph.base:

1. Prompt before overwrite (Step 2)
2. If user declines, keep existing
3. Human must manually merge changes if needed

Custom base files (not `graph.base`) are never touched by schema sync.
