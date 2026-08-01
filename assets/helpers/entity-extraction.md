# Entity Extraction Helper

## Purpose

Extract metadata from code files to create entity node documents.

## Extraction Process

### Step 1: Identify Entity Type

| Code Structure       | Entity Type | Category     |
| -------------------- | ----------- | ------------ |
| Module with classes  | entity      | module       |
| Single class         | entity      | class        |
| Single function      | entity      | function     |
| FastAPI/Flask router | entity      | api-endpoint |
| React/Vue component  | entity      | component    |

### Step 2: Extract Basic Metadata

| Field     | Source                                                              | Example                                                                  |
| --------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `name`    | Kebab-case from filename (no extension), prefixed with `{project}.` | `{project}.{kebab-case-from-filename}` e.g. `inference-api.auth-service` |
| `title`   | First `#` heading, class name, or filename                          | `AuthService`                                                            |
| `project` | CWD basename or git repo name, normalized to kebab-case             | `inference-api`                                                          |
| `agents`  | Current agent model                                                 | `deepseek`, `claude-opus-4-6`                                            |
| `tags`    | Inferred from path, imports, content                                | `auth`, `jwt`, `session`                                                 |

### Step 3: Infer Category

```regex
# Module: contains multiple exports or classes
(export\s+(class|function|const))|(from\s+\.+\s+import)

# Class: single class definition
class\s+\w+[:\(]

# Function: standalone function
(async\s+)?def\s+\w+\s*\(|function\s+\w+\s*\(

# API Endpoint: route decorators
@(get|post|put|delete|router\.(get|post|put|delete|patch))\s*\(

# Component: UI framework patterns
(React\.Component|@Component|defineComponent|Vue\.extend)
```

### Step 4: Infer Importance

| Importance | Indicators                                     |
| ---------- | ---------------------------------------------- |
| High       | Entry point, core business logic, auth/payment |
| Medium     | Utility, helper, shared module                 |
| Low        | Config, constant, minor helper                 |

**Heuristics:**

- Files in `auth/`, `payment/`, `core/` → high
- Files in `utils/`, `helpers/`, `lib/` → medium
- Files in `config/`, `constants/` → low
- Referenced by 5+ other files → high
- Referenced by 1-2 files → medium

### Step 5: Extract Related Entities

From imports:

```python
from auth.session import SessionManager  # → [[inference-api.session-manager]]
from payment.gateway import StripeClient  # → [[inference-api.stripe-client]]
```

From dependency injection:

```python
def __init__(self, db: Database, cache: Redis):
    # → [[inference-api.database]], [[inference-api.redis-cache]]
```

From docstrings/comments:

```python
"""
See [[inference-api.user-model]] for data structure.
Depends on [[inference-api.rate-limiter]] for throttling.
"""
```

## Trigger Pattern Generation

Generate `agent-context` triggers from file path:

| File Path                 | Trigger Pattern                           |
| ------------------------- | ----------------------------------------- |
| `src/auth/service.py`     | `pattern: "src/auth/**"`                  |
| `src/auth/` (directory)   | `pattern: "src/auth/**"`                  |
| `src/api/routes/users.py` | `pattern: "src/api/routes/users*"`        |
| Multiple files            | `pattern: "src/auth/**"` (broadest match) |

## Constraint Extraction

From docstrings:

```python
"""
All auth operations must go through AuthMiddleware.

Token refresh must be atomic.
"""
```

→ Extract:

```yaml
constraints:
  - "All auth operations must go through AuthMiddleware"
  - "Token refresh must be atomic"
```

From comments:

```python
# IMPORTANT: Never bypass auth middleware
# NOTE: Rate limit all endpoints
```

→ Extract:

```yaml
constraints:
  - "Never bypass auth middleware"
  - "Rate limit all endpoints"
```

## Pattern Extraction

From code structure, identify reusable patterns:

```python
@router.get("/users")
@require_auth
async def get_users(user: AuthenticatedUser = CurrentUser()):
    return await service.get_users(user.id)
```

→ Extract pattern:

```yaml
patterns:
  - name: "protected-endpoint"
    template: |
      @router.get("/{resource}")
      @require_auth
      async def get_{resource}(user: AuthenticatedUser = CurrentUser()):
          return await service.get_{resource}(user.id)
```

## Check Generation

Infer from file type:

| File Type    | Default Checks                                |
| ------------ | --------------------------------------------- |
| Python       | `pytest tests/{module}/`, `ruff check {path}` |
| TypeScript   | `npm test`, `eslint {path}`                   |
| API endpoint | Integration test command                      |

## Example Extraction

**Input file:** `src/auth/service.py`

```python
"""
Authentication service.

All auth operations must go through AuthMiddleware.
Token refresh must be atomic.
"""

from auth.session import SessionManager
from auth.jwt_handler import JWTHandler

class AuthService:
    """Core authentication logic."""

    def __init__(self, session: SessionManager, jwt: JWTHandler):
        self.session = session
        self.jwt = jwt

    @rate_limit(min_interval_ms=100)
    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        ...
```

**Extracted entity:**

```yaml
type: entity
name: inference-api.auth-service
category: module
importance: high  # auth is core
tags: [auth, jwt, session, token]
related:
  - "[[inference-api.session-manager]]"
  - "[[inference-api.jwt-handler]]"
```

**Generated agent-context:**

```yaml
triggers:
  - pattern: "src/auth/**"

constraints:
  - "All auth operations must go through AuthMiddleware"
  - "Token refresh must be atomic"

patterns:
  - name: "rate-limited-method"
    template: |
      @rate_limit(min_interval_ms={interval})
      async def {method_name}(self, {params}) -> {return_type}:
          ...

checks:
  - "Run: pytest tests/auth/"
  - "Run: ruff check src/auth/"
```

## Implementation Notes

1. Use `Read` to get file content
2. Apply regex patterns for extraction
3. Infer missing fields from context
4. Entity name = kebab-case module name; full identifier = `{project}.{name}`
5. Validate wiki-link format: `[[{project}.kebab-case-name]]`
