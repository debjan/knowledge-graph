# Mermaid UPDATE Operation

Regenerate Mermaid sequence diagrams after entity changes.

## Trigger

- Entity ADD, UPDATE, or DELETE operations completed
- Explicit "regenerate mermaid" or "update diagram" command
- User accepts offer to regenerate after entity changes

## When to Regenerate

Regeneration is needed when:

- New entities are added to the graph
- Entity relationships change (related field updates)
- Entities are deleted from the graph
- Entity types or categories change

## Workflow

### Step 1: Check for Existing Diagram

1. Resolve `{graph_path}` = `{vault}/Memory/{project}/`
2. Check if `graph-sequence.md` or `graph-relationships.md` exists:

```
Read("{graph_path}/graph-*.md")
```

3. If not exists, defer to ADD operation

### Step 2: Collect Current Entity Data

Scan all entity folders:

```
{graph_path}/entities/*.md
{graph_path}/concepts/*.md
{graph_path}/decisions/*.md
{graph_path}/constraints/*.md
{graph_path}/processes/*.md
```

For each entity, extract:

- Name (from filename or frontmatter `name`)
- Type (from folder name)
- Related entities (from frontmatter `related`)

### Step 3: Regenerate Sequence Diagram

1. Read [template](../templates/entity-interactions.md)
2. Build participant list from current entities
3. Build interaction flows from `related` fields
4. Include operation flows (ADD/UPDATE/DELETE lifecycle)

### Step 4: Regenerate Relationship Graph

1. Read [template](../templates/graph-relationships.md)
2. Build node list from current entities
3. Build edges from `related` fields
4. Apply styling by entity type/importance
5. Include cycle detection markup if needed

### Step 5: Validate Syntax

Before writing, validate Mermaid syntax:

1. **No list syntax conflicts**: Check for `[N. Item]` patterns
2. **Proper participant naming**: Use `participant ID as Display Name` format
3. **Valid arrow syntax**: Use `->>`, `-->>`, `--x`
4. **No emoji**: Replace with text labels

[Reference](../helpers/syntax-validation.md)

### Step 5: Write with Timestamp

Update timestamp in output:

```
<!-- Generated: YYYY-MM-DD HH:MM:SS -->
{mermaid code}
```

### Step 6: Report Results

```
✓ Regenerated graph-sequence.md
  - {entity_count} entities
  - {relationship_count} relationships
```

## Automatic Regeneration Triggers

### On Entity ADD

After creating a new entity:

1. Check if `graph-sequence.md` exists
2. If yes: Regenerate sequence diagram with new entity
3. Include new timestamp

### On Entity UPDATE

After updating an entity:

1. Check if `graph-sequence.md` exists
2. If yes: Regenerate sequence diagram (relationships may have changed)
3. Include new timestamp

### On Entity DELETE

After deleting an entity:

1. Regenerate sequence diagram (entity removed from participants)
2. Remove any interactions involving deleted entity
3. Include new timestamp

## Human Customization Preservation

If human has modified `graph-sequence.md`:

1. Prompt before overwrite
2. If user declines, keep existing
3. Human must manually merge changes if needed

Custom diagram files (not `graph-sequence.md`) are never touched by regeneration.

## Manual Regeneration Request

User can request regeneration explicitly:

> Regenerate the mermaid diagram

Response: Execute Step 1 through 6 without detecting changes first.
