---
type: entity
category: module
importance: high
status: active
project: inference-api
created: 2026-04-05
updated: 2026-04-05
agents:
  - deepseek
tags:
  - auth
  - jwt
  - session
  - security
related:
  - "[[session-manager]]"
  - "[[jwt-handler]]"
  - "[[rate-limiter]]"
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

# Auth Module

Handles all authentication and authorization logic. Provides token-based auth, session management, and rate limiting.

## Description

The auth module provides:

- Token-based authentication (JWT)
- Session management via Redis
- Role-based access control
- Rate limiting for auth endpoints

## Agent Context

```agent-context
triggers:
  - pattern: "src/auth/**"
  - pattern: "*auth*"
  - pattern: "*login*"
constraints:
  - "All auth operations must use AuthMiddleware"
  - "Never access session store directly — use SessionManager"
  - "Token refresh must be atomic"
patterns:
  - name: "protected-endpoint"
    description: "Standard pattern for protecting an API endpoint"
    template: |
      @router.get("/resource")
      @require_auth
      async def get_resource(user: AuthenticatedUser = CurrentUser()):
          return await service.get_resource(user.id)
checks:
  - "Run: pytest tests/auth/"
  - "Run: ruff check src/auth/"
  - "Verify: no hardcoded secrets"
```

## Implementation Files

- `src/auth/__init__.py` — Module exports
- `src/auth/service.py` — Core authentication logic
- `src/auth/middleware.py` — Request protection
- `src/auth/jwt_handler.py` — Token creation/validation
- `src/auth/decorators.py` — Auth decorators

## Related Entities

- [[session-manager]] — Handles session lifecycle
- [[jwt-handler]] — Token creation/validation
- [[rate-limiter]] — Request throttling

## Referencias

**Parent:** [[index]]
**Depends on:** [[redis-cache]]
