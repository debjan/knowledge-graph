# VERIFY Operation — Graph Integrity Verification

## When to Use This Operation

- User says "verify graph", "check graph integrity", "validate knowledge graph"
- After a SYNC operation (auto-run on completion)
- After manual ADD/UPDATE/DELETE operations
- When user reports broken links or inconsistent graph state
- Before committing graph changes to version control

## When NOT to Use This Operation

- User wants to sync graph from codebase (use SYNC operation)
- User wants to check entity health/lifecycle (use Health Check)
- User wants to load context (use QUERY operation)

## Critical Rules

### RULE 1: READ-ONLY

> VERIFY never modifies any files. It only reads and reports. Fixes are proposed as actionable suggestions but never auto-applied.

### RULE 2: COMPREHENSIVE COVERAGE

> ALL files in the graph directory must be checked, not just entity files. Concepts, decisions, constraints, processes, and {project}.index.md are all part of the graph.

### RULE 3: REPORT EVERY ISSUE

> Every discovered issue must be reported. Do not silently skip or fix issues — present them all for user action.

## Workflow

### Step 1: Resolve Paths

```
{graph_path} = {vault}/{memory}/{project}/
```

If ambiguous, enforce [Critical Rule 1](../../SKILL.md#rule-1-resolve-paths-once)

### Step 2: Run Verification Checks

Run all eight checks sequentially. Each check produces PASS/FAIL with details.

---

#### CHECK 1: Wiki-Link Resolution

**What it does:** Every `[[{project}.target]]` in every file must point to an existing file in the graph.

**Files scanned:** All `.md` and `.base` files in `{graph_path}` (recursive, excluding `chats/` and `node_modules/`)

**Resolution rules:**

| Link Format                   | Resolves To                                                                                                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[[{project}.{name}]]`        | `{graph_path}/{type}/{project}.{name}.md` across `entities/`, `concepts/`, `decisions/`, `constraints/`, `processes/`, or a root artifact `{graph_path}/{project}.{name}.md` / `{graph_path}/{project}.{name}.base` |
| `[[{project}.{name}\|Alias]]` | Same as above, displayed as "Alias"                                                                                                                                                                                 |

> The `{project}.` prefix is mandatory (RULE 8). An unprefixed link like `[[name]]` or `[[name\|Alias]]` is reported as a namespace violation by CHECK 8.

**Output:**

```
CHECK 1: Wiki-Link Resolution ──────────────────────────────────

PASS: All wiki-links resolve to existing files.
```


FAIL: 3 unresolved wiki-links found:

```
| File                                | Broken Link                                       |
| ----------------------------------- | ------------------------------------------------- |
| acp.index.md                        | [[acp.graph.base]] → file not found               |
| entities/acp.daemon.md              | [[acp.daemon-state]] → file not found             |
| concepts/acp.daemon-architecture.md | [[acp.daemon-lifecycle-process]] → file not found |

```

**Fix suggestions:**

- `[[acp.graph.base]]` in `acp.index.md` — ensure `acp.graph.base` exists, or fix the link
- `[[acp.daemon-state]]` in `entities/acp.daemon.md` — entity was deleted, remove or redirect the link
- `[[acp.daemon-lifecycle-process]]` in `concepts/acp.daemon-architecture.md` — concept was renamed, update the link

---

#### CHECK 2: Bidirectional Backlinks

**What it does:** For every `[[{project}.target]]` in a file's `related:` frontmatter field, the target's `related:` field must contain a reciprocal `[[{project}.source]]`.

**Files scanned:** All `.md` files with frontmatter in `{graph_path}`

**Verification algorithm:**

```

For each file A in graph:
  For each [[{project}.target]] in A.related:
    Read target file B
    If [[{project}.A]] not in B.related:
      FAIL: missing backlink from B to A

```

**Output:**

```

CHECK 2: Bidirectional Backlinks ──────────────────────────────

PASS: All {n} related entries are bidirectional.

```

```

FAIL: 2 missing backlinks detected:

| Source Entity               | Target Entity       | Missing In                  |
| --------------------------- | ------------------- | --------------------------- |
| [[acp.daemon]]              | [[acp.permissions]] | entities/acp.permissions.md |
| [[acp.daemon-architecture]] | [[acp.daemon]]      | entities/acp.daemon.md      |

Missing from entity [[acp.permissions]] (related):

- "[[acp.daemon]]"

```

**Fix suggestions:**

- Add `- "[[acp.daemon]]"` to `entities/acp.permissions.md` related field
- Add `- "[[acp.daemon-architecture]]"` to `entities/acp.daemon.md` related field

---

#### CHECK 3: Duplicate Related Entries

**What it does:** A `related:` list must not contain duplicate entries for the same target.

**Output:**

```

CHECK 3: Duplicate Related Entries ─────────────────────────────

PASS: No duplicates found in any related field.

```

```

FAIL: 1 file has duplicate related entries:

| File                                     | Duplicate Target                            |
| ---------------------------------------- | ------------------------------------------- |
| constraints/acp.sublime-thread-safety.md | [[acp.daemon-architecture]] appears 2 times |

```

**Fix suggestions:**

- Remove one duplicate `[[acp.daemon-architecture]]` entry from `constraints/acp.sublime-thread-safety.md`

---

#### CHECK 4: Implementation Files Existence

**What it does:** Every file listed in an entity's `implementation_files` field must exist on disk.

**Output:**

```

CHECK 4: Implementation Files Existence ────────────────────────

PASS: All implementation files exist on disk.

```

```

FAIL: 2 entities reference missing files:

| Entity         | Missing File                                                      |
| -------------- | ----------------------------------------------------------------- |
| [[acp.daemon]] | modules/daemon_state.py (consolidated into modules/daemon.py)     |
| [[acp.daemon]] | modules/daemon_lifecycle.py (consolidated into modules/daemon.py) |

Stale files count: 2

```

**Fix suggestions:**

- Update `acp.daemon` implementation_files to `["modules/daemon.py"]` and set `health.needs_update = true`

---

#### CHECK 5: Frontmatter Completeness

**What it does:** Every entity and graph file must have a complete and valid frontmatter block.

**Required fields per type:**

| Type       | Required Fields                                                                                                                     |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| entity     | `type`, `name`, `category`, `importance`, `status`, `project`, `created`, `updated`, `agents`, `tags`, `related`, `health`, `usage` |
| concept    | `type`, `name`, `category`, `importance`, `status`, `created`, `updated`, `related`                                                 |
| decision   | `type`, `name`, `title`, `status`, `created`, `updated`, `related`                                                                  |
| constraint | `type`, `name`, `category`, `importance`, `status`, `created`, `updated`, `related`                                                 |
| process    | `type`, `name`, `category`, `importance`, `status`, `created`, `updated`, `related`                                                 |

**Health sub-fields:**

```yaml
health:
  stale_files: []
  last_verified: {date}
  needs_update: false
  needs_delete: false
```

**Output:**

```
CHECK 5: Frontmatter Completeness ────────────────────────────

PASS: All {n} files have complete frontmatter.
```


FAIL: 3 files missing required fields:

```
| File                                      | Missing Fields                            |
| ----------------------------------------- | ----------------------------------------- |
| entities/acp.plugin.md                    | health.last_verified, health.needs_update |
| entities/acp.ui.md                        | health.last_verified                      |
| processes/acp.daemon-lifecycle-process.md | health (missing entirely)                 |

```

**Fix suggestions:**

- Add `health.last_verified: 2026-07-22` and `health.needs_update: false` to `entities/acp.plugin.md`
- Add `health.last_verified: 2026-07-22` to `entities/acp.ui.md`
- Add health block to `processes/acp.daemon-lifecycle-process.md`

---

#### CHECK 6: Updated Date Freshness

**What it does:** Ensure every file has an `updated` field that is not stale (> 90 days from today).

**Output:**

```

CHECK 6: Updated Date Freshness ────────────────────────────────

PASS: All {n} files have current updated dates.

```

```

FAIL: 1 file has stale updated date:

| File                   | Last Updated | Days Ago |
| ---------------------- | ------------ | -------- |
| entities/acp.plugin.md | 2026-04-05   | 108      |

```

**Fix suggestions:**

- Review and update `entities/acp.plugin.md`, then set `updated: {today}`

---

#### CHECK 7: Changelog Consistency

**What it does:** For files with a `changelog` field, verify that version strings increment and dates are chronological.

**Output:**

```

CHECK 7: Changelog Consistency ─────────────────────────────────

PASS: All changelogs are consistent.

```

```

FAIL: 1 file has inconsistent changelog:

| File                   | Issue                         |
| ---------------------- | ----------------------------- |
| entities/acp.daemon.md | version 2.0 → 2.0 (duplicate) |

```

**Fix suggestions:**

- Fix version sequence in `entities/acp.daemon.md` changelog

---

#### CHECK 8: Namespace Conformance

**What it does:** Every wiki-link and every node filename must carry the `{project}.` namespace prefix (RULE 8). Any unprefixed link or unprefixed node file is a FAIL.

**Files scanned:** All `.md` and `.base` files in `{graph_path}` (recursive, excluding `chats/` and `node_modules/`)

**Rules:**

| Item                   | Must Match                                                                                                             | Fail If                                                        |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Wiki-link              | `[[{project}.{name}]]` or `[[{project}.{name}\|Alias]]`                                                                | `[[name]]` / `[[name\|Alias]]` without the `{project}.` prefix |
| Root artifact link     | `[[{project}.index]]`, `[[{project}.graph.base]]`, `[[{project}.graph-sequence]]`, `[[{project}.graph-relationships]]` | Any unprefixed root reference                                  |
| Node filename          | `{project}.{name}.md` inside `entities/`, `concepts/`, `decisions/`, `constraints/`, `processes/`                      | Any `.md` not starting with `{project}.` in those folders      |
| Root artifact file     | `{project}.index.md`, `{project}.graph.base`, `{project}.graph-sequence.md`, `{project}.graph-relationships.md`        | Unprefixed root artifact files                                 |
| `name:` frontmatter    | Equals `{project}.{name}`                                                                                              | Any unprefixed `name:` value                                   |
| `project:` frontmatter | Equals `{project}` (short kebab-case id)                                                                               | Missing or mismatched project id                               |

**Output:**

```

CHECK 8: Namespace Conformance ────────────────────────────────

PASS: All links and files carry the {project}. prefix.

```

```

FAIL: 3 issues found:

| File                     | Issue                                                               |
| ------------------------ | ------------------------------------------------------------------- |
| entities/auth-service.md | filename missing "{project}." prefix (expected acp.auth-service.md) |
| entities/acp-daemon.md   | link [[acp-daemon]] should be [[acp.daemon]]                        |
| index.md                 | filename missing "{project}." prefix (expected acp.index.md)        |

```

**Fix suggestions:**

- Rename `entities/auth-service.md` → `entities/acp.auth-service.md` and update `name:` + backlinks.
- Replace `[[acp-daemon]]` with `[[acp.daemon]]` (update `related` fields and backlinks).
- Rename `index.md` → `acp.index.md` and fix `[[index]]` → `[[acp.index]]`.

### Step 3: Aggregate Report

Compile all check results into a single summary:

```
### Graph Integrity Report

**Graph:** {graph_path}
**Total files:** 25 (14 entities, 2 concepts, 2 decisions, 1 constraint, 2 processes, 4 root)
**Last verified:** {today}

#### Results Summary

| Check                        | Status | Issues |
| ---------------------------- | ------ | ------ |
| 1. Wiki-Link Resolution      | PASS   | —      |
| 2. Bidirectional Backlinks   | PASS   | —      |
| 3. Duplicate Related Entries | FAIL   | 1      |
| 4. Implementation Files      | FAIL   | 2      |
| 5. Frontmatter Completeness  | PASS   | —      |
| 6. Updated Date Freshness    | PASS   | —      |
| 7. Changelog Consistency     | PASS   | —      |
| 8. Namespace Conformance     | PASS   | —      |

**Overall: ⚠️ 2 checks failing — see details above**

#### Suggested Actions

1. Remove duplicate `[[acp.daemon-architecture]]` from `constraints/acp.sublime-thread-safety.md`
2. Update `acp.daemon` implementation_files to `["modules/daemon.py"]`

[Fix All] [Fix Selected] [Dismiss]

```

### Step 4: Offer Fixes

After presenting the report, offer to fix the issues:

- **Fix All** — Apply all suggested fixes without further confirmation
- **Fix Selected** — Walk through each issue individually
- **Dismiss** — Leave all issues for later

If the user selects Fix All or Fix Selected:

1. Apply fixes using the appropriate operation (UPDATE for entity changes, DELETE for stale entities)
2. Re-run VERIFY to confirm all issues are resolved
3. Report final status

### Step 5: Re-Verify (Optional)

If fixes were applied, offer to re-run verification:

```
Fixes applied. Re-run VERIFY to confirm? [Yes] [Skip]
```

## Best Practices

- Run VERIFY after every SYNC operation to catch any inconsistencies from bulk operations
- Run VERIFY before committing graph changes to version control
- Address CHECK 1 (broken links) and CHECK 2 (missing backlinks) first — they break graph navigation
- CHECK 4 (missing implementation files) often indicates a STALE entity that needs UPDATE or DELETE
- CHECK 8 (namespace conformance) must be run after any bulk rename or migration to confirm every link and file carries the `{project}.` prefix
- Run VERIFY when onboarding to a new project to understand graph health before making changes

## See Also

**Related Operations:**

- [SYNC](./SYNC.md) — Bulk graph sync from codebase
- [ADD](./ADD.md) — Create new entities
- [UPDATE](./UPDATE.md) — Modify existing entities
- [DELETE](./DELETE.md) — Remove entities

**Related Assets:**

- [lifecycle-management.md](../helpers/lifecycle-management.md) — Health check and lifecycle
