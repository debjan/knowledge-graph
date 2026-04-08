# Base ADD Operation

Create Obsidian Bases dashboard files for knowledge graph projects.

## Trigger

- First entity creation in a new project (called from [ADD operation](../../ops/ADD.md) Step 10)
- Explicit "create base" or "generate dashboard" command

## Prerequisites

- Entity directory structure exists at `Memory/{project}/`
- Templates available at [templates](../templates/)

## Workflow

### Step 1: Resolve Paths

```
vault = resolved vault path
project = resolved project name
graph_path = {vault}/Memory/{project}
```

### Step 2: Create Project Dashboard (graph.base)

1. Check if `graph.base` exists:

```
Read("{graph_path}/graph.base")
```

2. If not exists, create from template:

```
Read("assets/bases/templates/graph-base.yaml")
Write("{graph_path}/graph.base", template_content)
```

3. If exists, prompt:

```
graph.base already exists for this project.
[Skip] — Keep existing dashboard
[Update] — Regenerate from template
```

### Step 3: Report Results

```
✓ Created graph.base (project dashboard)
```

Or if skipped:

```
(Dashboard skipped — {reason})
```

## Template Content

### graph.base

Per-project dashboard with:

- **Filters:** In-folder checks for all entity types (entities, concepts, decisions, constraints, processes)
- **Formulas:**
  - `days_since_used` — Days since last usage
  - `health_status` — Visual health indicator (Delete/Update/OK)
  - `activity_level` — Usage activity (Active/Used/Never)
- **Views:**
  - Overview table
  - Needs Attention table (filtered by health flags)
  - By Category cards
  - Recent Activity table

## Human Customization

- Humans can customize base files (add views, change formulas)
- Skill prompts before overwriting: "Update graph.base to match template?"
- Custom `.base` files (not `graph.base`) are never touched by skill

## Error Handling

- **Template not found**: Error, cannot proceed
- **Write failed**: Error with path details
