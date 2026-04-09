---
type: concept
category: pattern
importance: high
status: active
project: my-project
created: 2026-04-05
updated: 2026-04-05
agents:
  - deepseek
tags:
  - pattern
  - data-access
  - architecture
  - repository
related:
  - "[[database-module]]"
  - "[[unit-of-work]]"
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

# Repository Pattern

Abstracts data access logic behind a common interface. All data operations go through repository classes, not direct database calls.

## Description

The Repository Pattern provides:

- Abstraction layer between business logic and data access
- Consistent interface for CRUD operations
- Easier testing via mock repositories
- Centralized query logic

## Agent Context

```agent-context
triggers:
  - pattern: "*repository*"
  - pattern: "*/data/*"
constraints:
  - "Never access database directly from services — use repositories"
  - "Each aggregate root gets its own repository"
  - "Repositories only handle read/write, not business logic"
patterns:
  - name: "repository-class"
    description: "Standard repository structure"
    template: |
      class {Entity}Repository:
          def __init__(self, db: Database):
              self.db = db

          async def get(self, id: str) -> {Entity}:
              ...

          async def save(self, entity: {Entity}) -> None:
              ...

          async def delete(self, id: str) -> None:
              ...
```

## Examples

### Example 1: User Repository

```python
class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    async def get(self, user_id: str) -> User:
        return await self.db.users.find_one({"id": user_id})

    async def save(self, user: User) -> None:
        await self.db.users.update_one(
            {"id": user.id},
            {"$set": user.dict()},
            upsert=True
        )
```

## Related Entities

- [[database-module]] — Database connection management
- [[user-service]] — Uses UserRepository

## References

**Applies to:** [[user-service]], [[order-service]], [[payment-service]]
**Related concepts:** [[unit-of-work]], [[domain-driven-design]]
