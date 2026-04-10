# Agent Context Block Specification

**Version:** 1.0
**Last updated:** 2026-04-05

This is the authoritative specification for `agent-context` executable blocks used in knowledge graph entity documents.

## Overview

Agent context blocks are YAML-formatted code blocks that provide structured, machine-readable instructions for AI agents. They define:

- **Triggers**: When to load this entity's context
- **Constraints**: Rules that MUST be followed
- **Patterns**: Code templates that SHOULD be used
- **Checks**: Commands to run after changes

## Syntax

### Block Format

```agent-context
triggers:
  - pattern: "src/auth/**"

constraints:
  - "Rule text"

patterns:
  - name: "pattern-name"
    template: |
      # Code here

checks:
  - "Run: command"
```

**Requirements:**

- Must use triple backticks with `agent-context` language identifier
- Content must be valid YAML
- Block must be terminated with triple backticks

## Fields

### triggers (Required)

Array of trigger patterns that cause this entity to be loaded.

```yaml
triggers:
  - pattern: "src/auth/**"        # Glob pattern
  - pattern: "*service*"          # Wildcard
  - pattern: "path/to/file.py"    # Specific file
```

**Rules:**

- At least one trigger is required
- Each trigger must have a `pattern` field
- Patterns use glob syntax: `*`, `**`, `?`

### constraints (Optional)

Array of hard rules that MUST be followed.

```yaml
constraints:
  - "All auth operations must use AuthMiddleware"
  - "Never access session store directly"
  - "Token refresh must be atomic"
```

**Rules:**

- Each constraint is a human-readable string
- Constraints are normative (MUST follow)
- Agent should not proceed if constraints cannot be satisfied

### patterns (Optional)

Array of code templates that SHOULD be used.

```yaml
patterns:
  - name: "protected-endpoint"
    description: "Standard pattern for protected endpoints"
    template: |
      @router.get("/resource")
      @require_auth
      async def get_resource(user: AuthenticatedUser = CurrentUser()):
          return await service.get_resource(user.id)
```

**Fields:**

| Field         | Required | Description                       |
| ------------- | -------- | --------------------------------- |
| `name`        | Yes      | Identifier for the pattern        |
| `description` | No       | When to use this pattern          |
| `template`    | Yes      | Code template as multiline string |

**Rules:**

- Templates are guidance (SHOULD use)
- Agent adapts placeholders to specific needs
- Multiple patterns can be defined

### checks (Optional)

Array of verification commands to run after changes.

```yaml
checks:
  - "Run: pytest tests/auth/"
  - "Run: ruff check src/auth/"
  - "Verify: no hardcoded secrets in code"
```

**Prefixes:**

| Prefix    | Meaning                  |
| --------- | ------------------------ |
| `Run:`    | Shell command to execute |
| `Verify:` | Manual verification step |

**Rules:**

- Checks run after entity is modified
- Agent should execute all checks before considering work complete
- Failed checks should be reported to user

## Complete Example

```agent-context
triggers:
  - pattern: "src/auth/**"
  - pattern: "*auth*"
  - pattern: "*login*"
  - pattern: "*session*"

constraints:
  - "All auth operations must use AuthMiddleware"
  - "Never access session store directly — use SessionManager"
  - "Token refresh must be atomic (no partial state)"
  - "Rate limit all auth endpoints (min 100ms between requests)"

patterns:
  - name: "protected-endpoint"
    description: "Standard pattern for protecting an API endpoint"
    template: |
      @router.get("/resource")
      @require_auth
      async def get_resource(user: AuthenticatedUser = CurrentUser()):
          return await service.get_resource(user.id)

  - name: "token-refresh"
    description: "Atomic token refresh with rollback"
    template: |
      async def refresh_tokens(refresh_token: str) -> TokenPair:
          async with redis.pipeline() as pipe:
              try:
                  result = await jwt.rotate(refresh_token)
                  await pipe.set(f"session:{result.session_id}", result.json())
                  await pipe.execute()
                  return result
              except Exception as e:
                  await pipe.reset()
                  raise RefreshError(str(e))

checks:
  - "Run: pytest tests/auth/"
  - "Run: ruff check src/auth/"
  - "Verify: no hardcoded secrets"
  - "Verify: token expiry times < 3600s"
```

## Parsing Rules

### YAML Extraction

1. Locate fenced code block with `agent-context` identifier
2. Extract content between backticks
3. Parse as YAML
4. Validate required fields

### Error Handling

| Error                      | Handling                         |
| -------------------------- | -------------------------------- |
| Missing `triggers`         | Reject block as invalid          |
| Invalid YAML               | Reject block, report parse error |
| Unknown field              | Warn but continue parsing        |
| Missing required sub-field | Reject pattern/constraint        |

## Validation Checklist

When creating/updating an agent-context block:

- [ ] Block uses `agent-context` language identifier
- [ ] Content is valid YAML
- [ ] `triggers` array exists with at least one pattern
- [ ] Each trigger has a `pattern` field
- [ ] Constraints are human-readable strings
- [ ] Patterns have `name` and `template` fields
- [ ] Checks use `Run:` or `Verify:` prefixes
- [ ] Block is properly terminated with triple backticks

## Version History

| Version | Date       | Changes               |
| ------- | ---------- | --------------------- |
| 1.0     | 2026-04-05 | Initial specification |
