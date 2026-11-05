# Safe Path Helper

## Purpose

Validate every identifier and path before it reaches a filesystem or shell command.

Entity names, project ids and relation names originate from user messages, code, or LLM output.
None of them are trusted. Unvalidated values placed into a path can escape `{graph_path}` (`../`),
and unvalidated values placed into a shell string can execute arbitrary commands
(`;`, `$()`, backticks, `--force`, spaces, globs).

Load this helper before **any** write, move, rename or delete: ADD, UPDATE, DELETE, RENAME, SYNC.

## When to Use

- Any `rm`, `mv`, `mkdir`, `git checkout` or `Write` targeting a graph path
- Any file path assembled from `{project}`, `{name}`, `{entity-name}`, `{related}`, `{old-name}`, `{new-name}`
- Any path derived from a user-provided entity name or a wiki-link target

## RULE S1: Identifier Allowlist

Identifiers are validated as **single path components** against an allowlist. Anything that does not match is rejected, never "cleaned up" or escaped.

Two different validation profiles apply, because two different things are being named.

| Identifier                                                                             | Profile      | Rule                                                                                 |
| -------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------ |
| `{project}`, `{name}`, `{entity-name}`, `{related}`, `{old-name}`, `{new-name}` | **created**  | `^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$` (lowercase kebab-case, 1-64 chars)          |
| `{memory}`                                                                             | **existing** | `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$` (single component; **case preserved** as detected) |
| `{type}`                                                                               | fixed        | one of `entities`, `concepts`, `decisions`, `constraints`, `processes`             |
| `{vault}`                                                                              | absolute     | absolute path, from `OBSIDIAN_VAULT`, discovery, or explicit user input               |

**Why two profiles.** The skill *creates* project ids and node names, so it can insist on lowercase kebab-case. It does **not** create the memory folder - that folder may already exist as `Memory`, `memory`, or `MEMORY`, and on a case-sensitive filesystem rewriting it silently produces a path that does not exist. So `{memory}` is validated as a safe single component while keeping its detected case verbatim.

Notes:

- Node and project names are normalized to lowercase kebab-case at creation time. Validation rejects uppercase rather than lowercasing silently. Include the ADR number in the name in lowercase: `adr-002-use-redis`, not `ADR-002`.
- A decision's human-readable form (`ADR-002: Use Redis for Session Storage`) belongs in the `title` field, never in the identifier. Identifiers stay machine-safe; titles may contain anything.
- A dot is only allowed as the `{project}.{name}` separator, never inside a component.
- 64 characters is a hard limit; longer names are rejected, not truncated.

## RULE S2: Rejected Input

Reject immediately, with no retry and no partial action, if any identifier contains:

| Category         | Rejected values                                                       |
| ---------------- | --------------------------------------------------------------------- |
| Traversal        | `..`, `.`, `/`, `\`, drive prefixes (`C:`), UNC prefixes (`\\server`) |
| Shell metachars  | `;` `&` `\|` `$` `` ` `` `<` `>` `(` `)` `{` `}` `[` `]` `*` `?` `!` `~` `#` `%` |
| Quoting/escaping | `"` `'` and backslash escapes                                         |
| Whitespace       | space, tab, newline, carriage return, NUL, any control character      |
| Option injection | any value starting with `-` (would be parsed as a flag, e.g. `--force`) |
| Absolute paths   | any value starting with `/`, `~`, or a drive/UNC prefix               |

Also reject identifiers that are empty, longer than 64 chars, or non-string.

## RULE S3: Path Containment

Building an allowed name is not enough. Confirm the final path stays inside the graph directory:

1. Resolve `{graph_path}` to an absolute path once (see [SKILL.md](../../SKILL.md#rule-1-resolve-paths-once)).
2. Build the target as `{graph_path}/{type}/{project}.{name}.md` from validated components only.
3. Normalize with `realpath` (resolves symlinks) and assert it is contained in `{graph_path}`.
4. Assert the final path still matches the expected template exactly.
5. Refuse to act when the target is a directory, a symlink pointing outside `{graph_path}`, a device file, or a hard link count greater than 1.

Containment check:

```python
from pathlib import Path

def resolve_target(graph_path: Path, node_type: str, project: str, name: str) -> Path:
    safe_component(project, "project")          # RULE S1/S2
    safe_component(name, "entity-name")
    if node_type not in NODE_TYPES:
        raise ValidationError(f"Invalid node type: {node_type!r}")

    root = graph_path.resolve(strict=True)
    target = (root / node_type / f"{project}.{name}.md").resolve(strict=False)

    if target.parent != (root / node_type).resolve(strict=False):
        raise ValidationError(f"Target escaped containment: {target}")
    if target.suffix != ".md":
        raise ValidationError(f"Target is not a markdown file: {target}")
    return target
```

## RULE S4: Safe Command Construction

Validation is the control. Quoting is defense in depth, never a substitute.

1. **Never interpolate raw user text into a shell string.** Build the command from validated components.
2. **Prefer structured arguments** when the tool accepts them (`Bash` args array, `Write(path=...)`), so no shell parses the value at all.
3. **Terminate option parsing** with `--` before any path argument.
4. **Never use** `rm -r`, `rm -rf`, `-f`, wildcarded paths, `eval`, `sh -c`, `bash -c`, `xargs`, or `find ... -delete` for graph operations.
5. **Never glob** entity paths. Expand nothing; operate on one resolved literal path.
6. **Single-quote** only after validation, and only if the shell requires quoting. Do not use double quotes for untrusted values, since `$` and backticks stay live inside them.
7. **Confirm before delete.** Validation does not replace user confirmation (DELETE RULE 1).

Allowed form:

```shell
# All components validated per RULE S1-S3 before this line runs
rm -- "{graph_path}/entities/{project}.{entity-name}.md"
```

Rejected forms and why:

```shell
rm {graph_path}/entities/{entity-name}.md            # unquoted: word splitting, globbing
rm "{graph_path}/entities/$NAME.md"                  # expansion of untrusted value
rm -rf "{graph_path}/entities/"                      # recursive force, unbounded blast radius
rm "$(echo {user_input})"                            # command substitution
find "{graph_path}" -name "{pattern}" -delete       # pattern-driven, unbounded
```

**Windows:** `rm` resolves to `Remove-Item`, which has no `--`. Use `-LiteralPath` so wildcards are not expanded, and never combine it with `-Recurse`:

```powershell
Remove-Item -LiteralPath "{graph_path}\entities\{project}.{entity-name}.md" -Confirm:$false
```

**Rollback commands** (`git checkout`, `git restore`) take the same treatment: validate the file path, pass it as a single argument, and prefix with `--`:

```shell
git checkout -- "{graph_path}/entities/{project}.{entity-name}.md"
```

## RULE S5: Fail Closed

If validation fails at any point:

- Abort the operation before touching the filesystem.
- Report the offending value verbatim (quoted, never executed) and the rule it violated.
- Do not fall back to "best effort" deletion, path trimming, or shell escaping.
- Ask the user for a valid kebab-case name instead.

## Post-Condition Checks

After every mutating step:

| Operation | Check                                                                 |
| --------- | --------------------------------------------------------------------- |
| Delete    | Target no longer exists; parent directory still exists                |
| Write     | Target exists and is inside `{graph_path}`                            |
| Rename    | New path exists, old path is gone or holds the tombstone              |

If a post-condition fails, report partial success. Never retry with a broader path or a recursive delete.

## Example: Safe DELETE

```
1. safe_component(project, "project")            -> acp
2. safe_component(entity_name, "entity-name")    -> daemon-state
3. resolve_target(graph_path, "entities", ...)   -> <vault>/memory/acp/entities/acp.daemon-state.md
4. assert inside <vault>/memory/acp/entities/    -> ok
5. assert not a directory / symlink / device     -> ok
6. user confirms deletion
7. rm -- "<resolved path>"
8. assert path no longer exists                  -> ok
```

If step 1 or 2 receives `../../.ssh/authorized_keys`, `acp; rm -rf ~`, or `--force`, the operation aborts at that step and nothing is deleted.

## See Also

- [SKILL.md](../../SKILL.md#rule-9-safe-identifiers-and-paths) - Parent rule
- [lifecycle-management.md](./lifecycle-management.md) - Entity health and lifecycle
- [DELETE.md](../ops/DELETE.md) - Delete workflow
- [RENAME.md](../ops/RENAME.md) - Rename workflow
