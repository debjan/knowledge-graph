# Base ADD Operation

Create Obsidian Bases (.base) dashboard for knowledge graph projects.

**Output Format:** MUST be valid YAML (not JSON) for .base files

## Trigger

- First entity creation in a new project (called from [ADD operation](../../ops/ADD.md) Step 13)
- Explicit "create base" or "generate dashboard" command

## Prerequisites

- Entity directory structure exists at `memory/{project}/`
- Templates available at [templates](../templates/)

## Workflow

### Step 1: Load `obsidian-bases` skill

### Step 2: Resolve Paths

```
vault = resolved vault path
project = resolved project name
graph_path = {vault}/memory/{project}
```

### Step 3: Create Project Dashboard (graph.base)

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

### Step 4: Validate YAML Output

**Before writing graph.base, validate:**

1. **Check YAML syntax**: Ensure valid YAML structure
2. **Check filters format**: Must use `and:`, `or:`, or `not:` NOT lists
3. **Check formulas**: All string formulas properly quoted
4. **Check properties**: All `formula.X` references have matching `X` in formulas section

**Validation errors to catch:**

- `filters: [{property: ...}]` ❌ → Must be `filters: {or: [...]}`
- Formulas with unescaped quotes
- Missing formula definitions

**Template variables:** Replace before output:

- `{project}` → actual project name
- `{graph_path}` → actual path

### Step 5: Validate with Obsidian CLI

**Requires:** `obsidian cli command`

After writing `graph.base`, validate the file:

```bash
obsidian base:views path="memory/{project}/graph.base"
```

**Expected output:**

- `✓ Valid YAML structure`
- `✓ All views parse correctly`
- `✓ Filters syntax valid`
- `✓ Formulas compile successfully`

**If validation fails:**

1. **If yamllint available:** Check YAML syntax: `yamllint {graph_path}/graph.base`
2. **Otherwise:** Check YAML manually (look for missing quotes, incorrect indentation, etc.)

### Step 6: Report Results

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
