---
type: decision
category: adr
importance: high
status: active
project: my-project
created: 2026-04-05
updated: 2026-04-05
agents:
  - deepseek
tags:
  - adr
  - session
  - redis
  - architecture
related:
  - "[[auth-module]]"
  - "[[session-manager]]"
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

# ADR-002: Use Redis for Session Storage

**Status:** Accepted
**Date:** 2026-04-05
**Decision Maker:** Team consensus

## Context

We need to store user session data for authentication. Sessions must be:

- Fast to read/write (sub-10ms latency)
- Persistent across server restarts
- Scalable for horizontal scaling
- Capable of TTL-based expiration

## Decision

We will use Redis as the session storage backend.

## Consequences

### Positive

- Sub-millisecond read latency
- Built-in TTL support for session expiration
- Horizontal scalability via Redis Cluster
- Proven reliability in production

### Negative

- Additional infrastructure dependency
- Memory cost for session storage
- Need to handle Redis connection failures

### Neutral

- Operations team needs Redis expertise

## Alternatives Considered

| Option         | Pros                 | Cons                    | Why Rejected           |
| -------------- | -------------------- | ----------------------- | ---------------------- |
| In-memory dict | Zero latency, simple | Lost on restart, no TTL | Not production-ready   |
| PostgreSQL     | Persistent, familiar | Higher latency, no TTL  | Too slow for auth      |
| MongoDB        | Persistent, flexible | Higher latency, complex | Overkill for simple KV |

## Agent Context

```agent-context
triggers:
  - pattern: "*session*"
  - pattern: "*redis*"
constraints:
  - "Session data must be stored in Redis, never in memory"
  - "Always set TTL on session keys"
```

## Related Entities

- [[auth-module]] — Uses sessions for auth
- [[session-manager]] — Redis session implementation

## Referencias

**Related:** [[ADR-001-database-choice]]
