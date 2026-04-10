# Entity Interactions Sequence Diagram Template

## Purpose

Generate a Mermaid sequence diagram showing interactions and message flows between entities.

## Template Structure

```mermaid
sequenceDiagram
    participant A as Entity A
    participant B as Entity B
    participant C as Entity C

    A->>B: Action/Message
    B->>C: Response/Request
    C-->>A: Callback/Result
```

## Generation Rules

1. **Participants**: Each entity becomes a participant
2. **Participant naming**: Use `participant ID as Display Name` format
3. **Message types**:
   - Solid arrow (`->>`) for synchronous calls
   - Dashed arrow (`-->>`) for responses/callbacks
   - Dotted arrow (`--x`) for failed/error messages
4. **Activation boxes**: Use `+` and `-` to show activation

## Syntax Validation Checklist

- [ ] No list syntax conflicts
- [ ] Participant names use valid identifiers (no spaces in IDs)
- [ ] Messages use proper arrow syntax (`->>`, `-->>`, `--x`)
- [ ] No emoji in participant names or messages
- [ ] Proper activation/deactivation pairing (`+`/`-`)

## Example Output

```mermaid
sequenceDiagram
    participant User
    participant KG as Knowledge Graph
    participant QE as Query Engine
    participant RS as Relevance Scorer

    User->>KG: Request context for file
    activate KG
    KG->>QE: Extract keywords
    activate QE
    QE-->>KG: Keywords list
    deactivate QE
    KG->>RS: Score entities
    activate RS
    RS-->>KG: Ranked entities
    deactivate RS
    KG-->>User: Context briefing
    deactivate KG
```

## Interaction Patterns

### ADD Operation Flow

```mermaid
sequenceDiagram
    participant User
    participant ADD as ADD Operation
    participant EE as Entity Extraction
    participant FS as File System

    User->>ADD: "Remember this entity"
    ADD->>EE: Extract entity data
    EE-->>ADD: Entity metadata
    ADD->>FS: Write entity file
    FS-->>ADD: File path
    ADD->>ADD: Regenerate Mermaid diagrams
    ADD-->>User: Entity created + diagrams updated
```

### QUERY Operation Flow

```mermaid
sequenceDiagram
    participant User
    participant QRY as QUERY Operation
    participant KG as Knowledge Graph
    participant RS as Relevance Scorer

    User->>QRY: "Load context for X"
    QRY->>KG: Find matching entities
    KG-->>QRY: Entity candidates
    QRY->>RS: Score relevance
    RS-->>QRY: Relevance scores
    QRY-->>User: Context briefing
```

## Output File Location

Generated sequence diagrams should be written to:
`Memory/{project}/graph-sequence.md`

## Timestamp Format

Include generation timestamp as HTML comment:
`<!-- Generated: YYYY-MM-DD HH:MM:SS -->`

## Cycle Visualization

### When to Show Cycles

When QUERY detects circular references (A ↔ B), note them in the diagram.

### Sequence Diagram Token

For sequence diagrams, add a note when participants form a cycle:

```mermaid
sequenceDiagram
    participant A
    participant B
    participant C

    Note over A,C: ⚠️ Circular dependency detected

    A->>B: references
    B->>C: references
    C->>A: ⚠️ back-reference (cycle)
```

### Relationship Graph (Better for Cycles)

For explicit cycle visualization, generate a **separate relationship graph** using `graph TD` or `graph LR`:

```mermaid
graph LR
    A[auth-module] --> B[session-manager]
    B --> C[jwt-handler]
    C --> A

    %% Cycle indicator: use different styling
    style A fill:#ffcccc
    style C stroke:#ff0000,stroke-width:3px
    linkStyle 0,1 stroke:#333
    linkStyle 2 stroke:#ff0000,stroke-width:3px,stroke-dasharray: 5 5
```

### Cycle Detection in Generation

When generating sequence diagrams from entity data:

1. Check for circular references in `related` fields
2. If cycle detected (A ↔ B or A → B → C → A):
   - Add `Note over A,B: ⚠️ Circular dependency`
   - Style flow arrows differently for cycle edges
   - Consider generating relationship graph alongside sequence diagram

### Code Example

```python
def detect_cycles(entities: List[Entity]) -> List[Tuple[str, str]]:
    cycles = []
    for entity in entities:
        for related in entity.related:
            related_entity = load_entity(related)
            if entity.name in related_entity.related:
                cycles.append((entity.name, related))
    return cycles

def add_cycle_indicators(mermaid_code: str, cycles: List[Tuple[str, str]]) -> str:
    for A, B in cycles:
        mermaid_code += f"\nNote over {A},{B}: Circular dependency"
    return mermaid_code
```

### Styling for Cycles

| Element            | Style                                  | Meaning                     |
| ------------------ | -------------------------------------- | --------------------------- |
| Cycle arrow        | `stroke:#ff0000,stroke-dasharray: 5 5` | Completion of cycle         |
| Cycle note         | `Note over` with ⚠️ emblem             | Warning indicator           |
| Cycle participants | `fill:#ffcccc`                         | Highlight involved entities |
