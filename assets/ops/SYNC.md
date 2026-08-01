# SYNC Operation — Bulk Reconcile Graph with Codebase

## When to Use This Operation

- User says "sync the graph", "synchronize with codebase", "update graph from codebase"
- After a large refactor (files moved, merged, renamed, deleted)
- When you need to bring the graph up to date with the current codebase state
- Before a health check or verification run

## When NOT to Use This Operation

- Single entity change (use ADD, UPDATE, or DELETE individually)
- User wants to query/load context (use QUERY operation)
- User wants to check health only (use Health Check)
- Codebase has not changed since last sync

## Critical Rules

### RULE 1: CONFIRM EACH CHANGE

> Never apply ADD, UPDATE, or DELETE without user confirmation per entity or per batch. Present the diff report and let the user decide.

### RULE 2: ATOMICITY PER ENTITY

> Each entity operation within a sync (ADD/UPDATE/DELETE) must follow that operation's atomicity rules. If one entity fails, the others should still complete — log partial results.

### RULE 3: AUTO-VERIFY AFTER SYNC

> Always run VERIFY operation after completing a sync to confirm graph integrity.

### RULE 4: PRESERVE FRONTMATTER ON UPDATE

> When updating existing entities, preserve usage statistics, changelog history, and health metadata unless explicitly stale.

## Workflow

### Step 1: Resolve Paths

Resolve `{vault}`, `{memory}`, `{project}`, and `{codebase}`:

```
{vault} = Obsidian vault root
{memory} = case-sensitive memory folder name
{project} = project name (codebase basename)
{graph_path} = {vault}/{memory}/{project}
{codebase} = project codebase root (working directory)
```

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

Load `obsidian-markdown` skill

### Step 2: Scan Codebase

Walk the codebase directory to discover all source files:

```
filesystem -> list of all *.py (or relevant source) files with:
  - relative path
  - line count
  - last modified time
  - imports/exports (for relationship detection)
```

**For Python projects:** scan `*.py` files excluding `__pycache__/`, `.venv/`, `node_modules/`, `.*`

**Source file patterns by project type:**

| Project Type  | Patterns                 |
| ------------- | ------------------------ |
| Python        | `**/*.py`                |
| JavaScript/TS | `**/*.{js,jsx,ts,tsx}`   |
| Rust          | `**/*.rs`                |
| Go            | `**/*.go`                |
| Java          | `**/*.java`              |
| Generic       | `**/*.{md,cfg,yaml,yml}` |

Group files by logical module:

- A single `*.py` file = 1 module
- An `__init__.py` + siblings = 1 package module
- Folders with `index.ts`/`mod.rs` = 1 module

### Step 3: Load Existing Entities

Read all existing entity files from `{graph_path}/entities/`:

```
For each .md file in {graph_path}/entities/:
  Extract: name, implementation_files, related, health status
```

Build a lookup map: `{module_name} -> {entity_metadata}`

### Step 4: Generate Diff Report

Compare codebase modules against existing entities to produce four categories:

#### CATEGORY A: NEW (code present, no entity)

A code module exists but has no corresponding entity file.

**Detection:** For each code module, check if an entity with `name` matching the module exists. If not, it's a new candidate.

**Heuristic for significance:** Skip if module is:

- A single file with < 20 lines of actual code
- A test file (`test_*.py`, `*_test.py`, `*.spec.*`, `*.test.*`)
- A config file (`.cfg`, `.ini`, `.toml`, `.yaml`)
- An `__init__.py` with only imports
- A `__main__.py` with only a CLI entry point

**Output:**

```
| Entity Name          | Source File                 | Lines | Type   |
| -------------------- | --------------------------- | ----- | ------ |
| [[acp.autocomplete]] | modules/acp_autocomplete.py | 45    | module |
| [[acp.logger]]       | modules/logger.py           | 30    | module |
```

#### CATEGORY B: CHANGED (entity exists, code changed)

An entity exists but its implementation files have changed (different line count, different content, file moved/renamed).

**Detection:** Compare `implementation_files` entries against filesystem:

- **File missing:** entity's implementation file no longer exists on disk
- **Line count changed:** code file line count differs from entity's recorded `lines`
- **Content changed:** imports, classes, or functions differ

**Output:**

```
| Entity              | Change            | Old Value               | New Value         |
| ------------------- | ----------------- | ----------------------- | ----------------- |
| [[acp.daemon]]      | File consolidated | 4 files                 | modules/daemon.py |
| [[acp.daemon]]      | Lines             | 23                      | 641               |
| [[acp.permissions]] | File renamed      | daemon_permissions.py   | permissions.py    |
| [[acp.daemon]]      | File missing      | modules/daemon_state.py | (deleted)         |

```

#### CATEGORY C: STALE (entity exists, code gone)

An entity exists but all its implementation files are missing from disk.

**Detection:** Entity has implementation files, none exist on filesystem.

**Output:**

```

| Entity                   | Missing Files                         |
| ------------------------ | ------------------------------------- |
| [[acp.daemon-state]]     | modules/daemon_state.py (deleted)     |
| [[acp.daemon-lifecycle]] | modules/daemon_lifecycle.py (deleted) |

```

#### CATEGORY D: ORPHAN (referenced but missing backlinks)

An entity is referenced by others but does not have reciprocal backlinks. See [VERIFY.md](./VERIFY.md) for detailed detection.

#### Diff Report Format

Collect all findings into a single tabular report:

```
### Graph Sync Diff Report

**Project:** acp
**Codebase:** 15 files scanned
**Existing entities:** 14
**Changes detected:** 8

#### NEW (2)

| Entity               | File                    | Lines | Type   |
| -------------------- | ----------------------- | ----- | ------ |
| [[acp.autocomplete]] | modules/autocomplete.py | 45    | module |

#### CHANGED (4)

| Entity              | Change | Old                   | New            |
| ------------------- | ------ | --------------------- | -------------- |
| [[acp.daemon]]      | Lines  | 23                    | 641            |
| [[acp.permissions]] | File   | daemon_permissions.py | permissions.py |

#### STALE (2)

| Entity               | Missing Files           |
| -------------------- | ----------------------- |
| [[acp.daemon-state]] | modules/daemon_state.py |

**Options:**

- [Review Each] — Walk through each change individually
- [Batch Apply] — Apply all changes with auto-generated updates
- [Skip] — Dismiss and do nothing

```

### Step 5: Process Changes

For each category, apply the corresponding operation:

#### CATEGORY A: ADD

For each NEW candidate, use the [ADD.md](./ADD.md) workflow:

1. Extract metadata using [entity-extraction.md](../helpers/entity-extraction.md)
2. Present entity preview to user
3. On confirmation, create entity file
4. Update bidirectional references

For batch ADD, present all candidates and confirm as a group:

```
### Batch ADD Confirmation

The following entities will be created:

| Entity               | File                    | Lines |
| -------------------- | ----------------------- | ----- |
| [[acp.autocomplete]] | modules/autocomplete.py | 45    |
| [[acp.logger]]       | modules/logger.py       | 30    |

[Confirm All] [Review Each] [Cancel]

```

#### CATEGORY B: UPDATE

For each CHANGED candidate, use the [UPDATE.md](./UPDATE.md) workflow:

1. Re-extract metadata from current code
2. Show diff (frontmatter, content, health)
3. Offer MERGE/OVERRIDE/CANCEL
4. On confirmation, apply update
5. Update bidirectional references if relations changed

For file renames/consolidations, update `implementation_files` and re-extract metadata.

#### CATEGORY C: DELETE

For each STALE candidate, use the [DELETE.md](./DELETE.md) workflow:

1. Show confirmation with related entities
2. On confirmation, clean bidirectional references
3. Delete entity file

**Warn about orphans:** If deleting an entity would leave related entities with no remaining relations, flag this.

#### CATEGORY D: ORPHAN

For each orphan issue, add the missing backlink to the target entity's `related` field.

### Step 6: Verify Integrity

After all changes are applied, automatically run [VERIFY.md](./VERIFY.md):

```

1. Check all wiki-links resolve
2. Check all backlinks are bidirectional
3. Check all implementation files exist
4. Check all entities have complete frontmatter

```

If VERIFY fails, report issues and offer to fix them (re-run verify after fixes).

### Step 7: Report Summary

```
### Graph Sync Complete

**Project:** {project}
**Files scanned:** {n}
**Entities before:** {n}

**Changes applied:**
- ADD: {n} entities created
- UPDATE: {n} entities updated
- DELETE: {n} entities deleted
- BACKLINK: {n} orphan references fixed

**Entities after:** {n}
**Graph integrity:** PASS (verified)

**Paths:**
- Entities: `{graph_path}/entities/`
- File count: {n} entities, {n} concepts, {n} decisions, {n} constraints, {n} processes
```

## Best Practices

- Run SYNC after every significant refactor (file moves, merges, renames, deletions)
- Always review the diff report before applying changes — the agent's automatic categorization may need human judgment
- For consolidation events (multiple files → one), prefer UPDATE on the surviving entity + DELETE on the consumed entities, then verify bidirectional references
- For rename events, use the RENAME operation on the entity rather than DELETE + ADD to preserve changelog history
- If the diff report shows too many false positives, tighten the significance heuristics (line count thresholds, file type filters)

## See Also

**Related Operations:**

- [ADD](./ADD.md) — Create new entities
- [UPDATE](./UPDATE.md) — Modify existing entities
- [DELETE](./DELETE.md) — Remove entities
- [RENAME](./RENAME.md) — Rename/move entities
- [VERIFY](./VERIFY.md) — Graph integrity verification

**Related Assets:**

- [entity-extraction.md](../helpers/entity-extraction.md) — Extract entity metadata
- [lifecycle-management.md](../helpers/lifecycle-management.md) — Bulk sync and lifecycle management
- [change-detection.md](../helpers/change-detection.md) — Code change heuristics
