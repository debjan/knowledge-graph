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
`Memory/{project}/{project}-sequence.md`

## Timestamp Format

Include generation timestamp as HTML comment:
`<!-- Generated: YYYY-MM-DD HH:MM:SS -->`
