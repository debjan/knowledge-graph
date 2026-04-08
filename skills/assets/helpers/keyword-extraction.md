# Keyword Extraction Helper

## Purpose

Extract keywords from entity metadata and current context for proactive retrieval.

## Keyword Sources

1. **ENTITY TRIGGERS** — pattern: `src/auth/service.py` → `["auth", "service"]`
2. **ENTITY TAGS** — tags: `[auth, jwt, session, token]` → direct use
3. **TASK DESCRIPTION** — "Fix the authentication token refresh bug" → `["authentication", "token", "refresh", "bug"]`
4. **OPEN FILES** — Current file paths → path components

## Extraction Methods

### From Triggers (Path Components)

Extract meaningful path components from glob patterns.

```python
def extract_from_trigger(pattern: str) -> list[str]:
    """
    Extract keywords from trigger pattern.

    "src/auth/service.py" → ["auth", "service"]
    "src/api/**" → ["api"]
    "*jwt*" → ["jwt"]
    """
    # Remove glob characters
    cleaned = pattern.replace("*", "").replace("/", " ").replace("\\", " ")

    # Split into components
    components = cleaned.split()

    # Filter common non-keywords
    stopwords = {"src", "lib", "app", "main", "index", "test", "spec", "util", "utils", "helper", "helpers"}
    keywords = [c.lower() for c in components if c.lower() not in stopwords and len(c) > 2]

    return keywords
```

**Examples:**

| Pattern                       | Keywords                               |
| ----------------------------- | -------------------------------------- |
| `src/auth/service.py`         | `["auth", "service"]`                  |
| `src/api/routes/users.py`     | `["api", "routes", "users"]`           |
| `*jwt*`                       | `["jwt"]`                              |
| `src/utils/helpers/format.py` | `["format"]` (utils, helpers filtered) |

### From Tags

Tags are already keywords — use directly.

```python
def extract_from_tags(tags: list[str]) -> list[str]:
    """
    Extract keywords from tags.

    ["auth", "jwt", "session"] → ["auth", "jwt", "session"]
    """
    return [tag.lower() for tag in tags]
```

### From Task Description

Extract meaningful words from task text.

```python
def extract_from_task(task: str) -> list[str]:
    """
    Extract keywords from task description.

    "Fix the authentication token refresh bug" → ["fix", "authentication", "token", "refresh", "bug"]
    """
    import re

    # Split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', task)

    # Filter stopwords
    stopwords = {"the", "for", "and", "with", "from", "this", "that", "have", "has", "will", "need", "should", "could"}
    keywords = [w.lower() for w in words if w.lower() not in stopwords]

    return keywords
```

**Examples:**

| Task                                       | Keywords                                               |
| ------------------------------------------ | ------------------------------------------------------ |
| "Fix the authentication token refresh bug" | `["fix", "authentication", "token", "refresh", "bug"]` |
| "Update the payment service to use stripe" | `["update", "payment", "service", "use", "stripe"]`    |
| "Add rate limiting to API endpoints"       | `["add", "rate", "limiting", "api", "endpoints"]`      |

### From Open Files

Extract from file paths currently being worked on.

```python
def extract_from_files(file_paths: list[str]) -> list[str]:
    """
    Extract keywords from file paths.

    ["src/auth/login.py", "src/utils/token.py"] → ["auth", "login", "token"]
    """
    all_keywords = []

    for path in file_paths:
        # Get filename without extension
        filename = path.split("/")[-1].split(".")[0]
        all_keywords.append(filename.lower())

        # Get directory names (excluding common ones)
        dirs = path.split("/")[:-1]
        stopwords = {"src", "lib", "app", "test", "tests"}
        for d in dirs:
            if d.lower() not in stopwords and len(d) > 2:
                all_keywords.append(d.lower())

    return list(set(all_keywords))
```

## Combining Keywords

### Merging Sources

```python
def extract_all_keywords(
    triggers: list[str],
    tags: list[str],
    task: str | None = None,
    files: list[str] | None = None
) -> list[str]:
    """
    Combine keywords from all sources.
    """
    keywords = set()

    # From triggers
    for pattern in triggers:
        keywords.update(extract_from_trigger(pattern))

    # From tags
    keywords.update(extract_from_tags(tags))

    # From task (if available)
    if task:
        keywords.update(extract_from_task(task))

    # From open files (if available)
    if files:
        keywords.update(extract_from_files(files))

    return list(keywords)
```

### Prioritization

Keywords from different sources have different weights:

| Source   | Priority | Rationale                     |
| -------- | -------- | ----------------------------- |
| Tags     | High     | User-curated, highly relevant |
| Triggers | Medium   | Derived from code structure   |
| Task     | Medium   | Current work context          |
| Files    | Low      | May be tangentially related   |

```python
def weight_keywords(keywords: dict[str, str]) -> dict[str, float]:
    """
    Weight keywords by source.

    {"auth": "tag", "service": "trigger"} → {"auth": 1.0, "service": 0.7}
    """
    weights = {
        "tag": 1.0,
        "trigger": 0.7,
        "task": 0.7,
        "file": 0.5
    }
    return {kw: weights[source] for kw, source in keywords.items()}
```

## Ripgrep Search Query

### Building Search Pattern

```python
def build_ripgrep_pattern(keywords: list[str]) -> str:
    """
    Build ripgrep search pattern from keywords.

    ["auth", "jwt", "token"] → "auth|jwt|token"
    """
    return "|".join(keywords)
```

### Search Command

```bash
rg -l -i "auth|jwt|token" --type code {project_path}
```

Flags:

- `-l`: List files only (not matching lines)
- `-i`: Case insensitive
- `--type code`: Limit to code files

### Timeout

Set timeout to avoid hanging on large codebases:

```python
import subprocess

result = subprocess.run(
    ["rg", "-l", "-i", pattern, "--type", "code", project_path],
    capture_output=True,
    text=True,
    timeout=5  # 5 second timeout
)
```

## Keyword Normalization

### Stemming

Reduce words to their stem for better matching:

```python
def stem_keywords(keywords: list[str]) -> list[str]:
    """
    Simple stemming (suffix removal).

    "authentication" → "auth"
    "services" → "service"
    """
    suffixes = ["ation", "tion", "sion", "ness", "ment", "ing", "ies", "es", "s"]
    stemmed = []

    for kw in keywords:
        for suffix in suffixes:
            if kw.endswith(suffix) and len(kw) > len(suffix) + 2:
                kw = kw[:-len(suffix)]
                break
        stemmed.append(kw)

    return list(set(stemmed))
```

**Examples:**

| Original       | Stemmed |
| -------------- | ------- |
| authentication | auth    |
| services       | service |
| running        | run     |
| verification   | verif   |

### Case Normalization

All keywords are lowercased:

```python
keywords = [kw.lower() for kw in keywords]
```

## Deduplication

```python
def dedupe_keywords(keywords: list[str]) -> list[str]:
    """
    Remove duplicates and near-duplicates.
    """
    unique = set()
    for kw in keywords:
        kw_lower = kw.lower()
        # Check if we already have a similar keyword
        if not any(existing.startswith(kw_lower[:4]) for existing in unique):
            unique.add(kw_lower)
    return list(unique)
```

## Integration Points

### Proactive Retrieval

```python
# Step 1: Extract keywords from entities
entity_keywords = []
for entity in entities:
    entity_keywords.extend(extract_from_trigger(entity.triggers))
    entity_keywords.extend(extract_from_tags(entity.tags))

# Step 2: Extract from current context
if task_description:
    entity_keywords.extend(extract_from_task(task_description))
if open_files:
    entity_keywords.extend(extract_from_files(open_files))

# Step 3: Dedupe
keywords = dedupe_keywords(entity_keywords)

# Step 4: Build ripgrep pattern
pattern = build_ripgrep_pattern(keywords)

# Step 5: Run ripgrep
matching_files = run_ripgrep(pattern, project_path)
```

### Entity Matching

After ripgrep returns files, match back to entities:

```python
def match_files_to_entities(files: list[str], entities: list[Entity]) -> list[Entity]:
    """
    Match files to entity triggers.
    """
    matched = []
    for entity in entities:
        for pattern in entity.triggers:
            if any(fnmatch(file, pattern) for file in files):
                matched.append(entity)
                break
    return matched
```

## Configuration

| Parameter            | Default | Description                    |
| -------------------- | ------- | ------------------------------ |
| `min_keyword_length` | 3       | Minimum characters for keyword |
| `max_keywords`       | 20      | Maximum keywords in search     |
| `ripgrep_timeout`    | 5       | Timeout in seconds             |
| `stopwords`          | [...]   | Words to exclude               |

## Best Practices

1. **Prioritize tags:** User-curated keywords are most relevant
2. **Filter stopwords:** Remove common directories and words
3. **Stem keywords:** Match "auth" and "authentication"
4. **Dedupe:** Avoid redundant searches
5. **Timeout:** Don't hang on large codebases
6. **Limit count:** Too many keywords reduces precision
