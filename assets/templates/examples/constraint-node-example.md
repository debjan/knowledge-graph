---
type: constraint
name: my-project.no-direct-database-access
category: gotcha
importance: high
status: active
project: my-project
created: 2026-04-05
updated: 2026-04-05
agents:
  - deepseek
tags:
  - database
  - architecture
  - security
related:
  - "[[my-project.database-module]]"
  - "[[my-project.user-service]]"
usage:
  last_used: 2026-04-05
  use_count: 1
  last_auto_query: null
health:
  stale_files: []
  last_verified: null
  needs_update: false
  needs_delete: false
changelog:
  - version: "1.0"
    date: 2026-04-05
    changes: ["Initial creation"]
---

# No Direct Database Access

Services must never bypass the repository layer to access the database directly.

## Description

Direct database access bypasses:

- Connection pooling management
- Query logging and auditing
- Transaction boundaries
- Test mocking capability

This constraint exists to maintain architecture integrity and enable proper testing.

## Impact

**Severity:** High
**Affected areas:** All services that interact with the database

## Root Cause

Previous incidents where direct database access caused:

- Connection pool exhaustion
- Unlogged data changes
- Untestable code paths

## Workaround

Use repository classes for all data access. If a repository method doesn't exist, create one.

## Agent Context

```agent-context
triggers:
  - pattern: "*service*"
  - pattern: "*/db/*"
constraints:
  - "Never import database client directly in services"
  - "All database queries must go through repository classes"
```

## Examples

### Example: Violation

```python
# WRONG: Direct database access
from db.client import database

async def get_user(user_id: str):
    return await database.users.find_one({"id": user_id})
# VIOLATION
```

### Example: Correct Usage

```python
# CORRECT: Use repository
from repositories.user_repository import UserRepository

async def get_user(user_id: str, user_repo: UserRepository):
    return await user_repo.get(user_id)
```

## Related Entities

- [[my-project.database-module]] — Database connection management
- [[my-project.user-repository]] — Proper data access layer

## References

**Applies to:** [[my-project.user-service]], [[my-project.order-service]], [[my-project.payment-service]]
