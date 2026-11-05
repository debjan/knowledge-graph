# ruff: noqa: C901, PLR0911, PLR0912

"""Validation harness for knowledge-graph node files.

Runs the mechanical half of the VERIFY operation (CHECK 1-10):

- CHECK 1  wiki-links resolve to an existing node
- CHECK 2  ``related`` entries are reciprocal
- CHECK 3  no duplicate entries in ``related``
- CHECK 4  ``implementation_files`` exist relative to the codebase
- CHECK 5  required frontmatter fields per node type (incl. ``health.*``)
- CHECK 6  ``updated`` is newer than 90 days (warning)
- CHECK 7  changelog versions and dates move forward
- CHECK 8  filenames, ``name:``, ``project:`` and links carry the project prefix
- CHECK 9  identifiers, path containment, symlinks, case collisions (RULE 9)
- CHECK 10 frontmatter/fence containment, invisible characters, Mermaid
           directives, and an inventory of ``agent-context`` commands (RULE 10)

Standard library only. ``PyYAML`` is used when installed for frontmatter
parsing and ``agent-context`` blocks; without it CHECK 5, 7 and part of CHECK 10
are skipped and reported as such.

Usage:
    python scripts/validate_graph.py <graph_path> [--json] [--strict]
                                     [--codebase <project-root>]

Exit codes:
    0  no errors (warnings allowed unless --strict)
    1  findings
    2  usage or path error
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

IDENTIFIER_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$')
NODE_DIRS = ('entities', 'concepts', 'decisions', 'constraints', 'processes')
TOP_LEVEL_DIRS = frozenset(NODE_DIRS) | {'chats'}
ARTIFACT_SUFFIXES = frozenset({'.md', '.base', '.canvas', '.json', '.yml', '.yaml'})
ROOT_ARTIFACT_RE = re.compile(r'^(?:index|graph|graph-[a-z0-9-]+)$')
KNOWN_FRONTMATTER_KEYS = frozenset(
    {
        'name',
        'type',
        'title',
        'project',
        'category',
        'importance',
        'status',
        'created',
        'updated',
        'agents',
        'tags',
        'related',
        'health',
        'usage',
        'changelog',
        'implementation_files',
        'summary',
        'redirect_to',
    }
)
FENCE_RE = re.compile(r'^(`{3,})(.*)$')
KEY_RE = re.compile(r'^([A-Za-z0-9_-]+):')
BIDI_AND_FORMAT_ALLOWED = frozenset({'\u200d'})
ALLOWED_CONTROL = frozenset({'\n', '\t', '\r'})


class ValidationError(ValueError):
    """Raised when an identifier, path, or value fails validation."""


@dataclass(frozen=True)
class Issue:
    check: str
    path: str
    message: str
    severity: str = 'error'  # "error" | "warning"


# ---------------------------------------------------------------------------
# Identifiers and paths (RULE 9 / CHECK 9)
# ---------------------------------------------------------------------------


def is_safe_identifier(value: object) -> bool:
    """True when ``value`` is a safe single path component."""
    return isinstance(value, str) and bool(IDENTIFIER_RE.fullmatch(value))


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _line_of(text: str, index: int) -> int:
    return text.count('\n', 0, index) + 1


def is_invisible(char: str) -> bool:
    """True for format/control characters that should never be stored."""
    if char in ALLOWED_CONTROL or char in BIDI_AND_FORMAT_ALLOWED:
        return False
    category = unicodedata.category(char)
    return category in {'Cf', 'Cc', 'Cs', 'Co', 'Cn'} or char == '\ufeff'


def _check_node_filename(rel: Path) -> str | None:
    """Return an error message when a node filename breaks RULE 8/9."""
    stem = rel.stem
    if '.' not in stem:
        return f'filename missing "{{project}}." prefix: {rel.name}'
    project, _, name = stem.partition('.')
    if not is_safe_identifier(project):
        return f'unsafe project id in filename: {rel.name}'
    if rel.parent.name in NODE_DIRS:
        if not is_safe_identifier(name):
            return f'unsafe node name in filename: {rel.name}'
    elif not ROOT_ARTIFACT_RE.fullmatch(name):
        return f'unexpected root artifact name: {rel.name}'
    return None


def case_collisions(names: Iterable[str]) -> list[tuple[str, str]]:
    """Return ``(duplicate, original)`` pairs that differ only by case."""
    seen: dict[str, str] = {}
    collisions: list[tuple[str, str]] = []
    for name in names:
        key = Path(name).name.casefold()
        if key in seen and seen[key] != name:
            collisions.append((name, seen[key]))
        else:
            seen.setdefault(key, name)
    return collisions


def scan_paths(graph_path: str | os.PathLike[str]) -> list[Issue]:
    """CHECK 9: validate every path under ``graph_path``."""
    root = Path(graph_path)
    issues: list[Issue] = []
    if not root.is_dir():
        return [Issue('CHECK 9', str(root), 'graph path is not a directory')]

    resolved_root = root.resolve()
    scanned_files: list[str] = []

    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if 'chats' in rel.parts or 'node_modules' in rel.parts:
            continue

        if path.is_symlink():
            try:
                resolved = path.resolve(strict=True)
            except OSError:
                issues.append(Issue('CHECK 9', str(rel), 'broken symlink'))
                continue
            if not _is_within(resolved, resolved_root):
                issues.append(Issue(
                    'CHECK 9',
                    str(rel),
                    f'symlink resolves outside graph: {resolved}',
                ))
            elif not resolved.is_file():
                issues.append(Issue(
                    'CHECK 9', str(rel), 'symlink does not point to a regular file'
                ))
            continue

        if path.is_dir():
            if len(rel.parts) == 1 and rel.name not in TOP_LEVEL_DIRS:
                issues.append(Issue(
                    'CHECK 9',
                    str(rel),
                    'unexpected directory inside graph',
                    severity='warning',
                ))
            continue

        suffix = path.suffix.lower()
        if suffix not in ARTIFACT_SUFFIXES:
            issues.append(Issue(
                'CHECK 9',
                str(rel),
                f'unexpected file type: {suffix or "(none)"}',
                severity='warning',
            ))
            continue
        if suffix == '.md' and (message := _check_node_filename(rel)):
            issues.append(Issue('CHECK 9', str(rel), message))
        scanned_files.append(str(rel))

    for duplicate, original in case_collisions(scanned_files):
        issues.append(Issue(
            'CHECK 9',
            duplicate,
            f'filename collides with {original} on case-insensitive filesystems',
            severity='warning',
        ))

    return issues


# ---------------------------------------------------------------------------
# Content containment (RULE 10 / CHECK 10)
# ---------------------------------------------------------------------------


def split_frontmatter(text: str) -> tuple[list[str], list[str]]:
    """Split a node into frontmatter lines and body lines.

    Raises :class:`ValidationError` for a BOM, a missing block, or an
    unterminated block.
    """
    if text.startswith('\ufeff'):
        raise ValidationError('file starts with a byte order mark (U+FEFF)')
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        raise ValidationError('missing frontmatter block')
    for index in range(1, len(lines)):
        if lines[index].strip() == '---':
            return lines[1:index], lines[index + 1 :]
    raise ValidationError('unterminated frontmatter block')


def _duplicate_keys(frontmatter: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for line in frontmatter:
        if not (match := KEY_RE.match(line)):
            continue
        key = match.group(1)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    return duplicates


def _fence_regions(lines: Sequence[str]) -> Iterator[tuple[int, int]]:
    """Yield ``(start, end)`` index pairs of fenced blocks (0-based, inclusive)."""
    opener: int | None = None
    opener_len = 0
    for index, line in enumerate(lines):
        if not (match := FENCE_RE.match(line)):
            continue
        ticks = len(match.group(1))
        trailing = match.group(2).strip()
        if opener is None:
            opener, opener_len = index, ticks
        elif ticks >= opener_len and not trailing:
            yield opener, index
            opener, opener_len = None, 0
    if opener is not None:
        yield opener, -1


def scan_fences(lines: Sequence[str]) -> list[tuple[int, str]]:
    """Return ``(line_number, message)`` for unbalanced or suspicious fences."""
    problems: list[tuple[int, str]] = []
    opener: int | None = None
    opener_len = 0
    for index, line in enumerate(lines):
        if not (match := FENCE_RE.match(line)):
            continue
        ticks = len(match.group(1))
        trailing = match.group(2).strip()
        if opener is None:
            opener, opener_len = index, ticks
        elif not trailing:
            if ticks < opener_len:
                problems.append((
                    index + 1,
                    f'closing fence is shorter than opener on line {opener + 1}',
                ))
            else:
                opener, opener_len = None, 0
    if opener is not None:
        problems.append((opener + 1, 'unterminated code fence'))
    return problems


def _scan_invisible(text: str) -> list[tuple[int, str]]:
    problems: list[tuple[int, str]] = []
    for index, char in enumerate(text):
        if is_invisible(char):
            name = unicodedata.name(char, f'U+{ord(char):04X}')
            problems.append((_line_of(text, index), f'invisible character {name}'))
    return problems


def _scan_leaked_keys(body: Sequence[str]) -> list[tuple[int, str]]:
    """Detect frontmatter keys that ended up in the body (early termination)."""
    problems: list[tuple[int, str]] = []
    in_fence = False
    for index, line in enumerate(body):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = KEY_RE.match(line)
        if match and match.group(1) in KNOWN_FRONTMATTER_KEYS:
            problems.append((
                index + 1,
                f'frontmatter key {match.group(1)!r} found in body (block may have ended early)',
            ))
    return problems


def iter_agent_context(lines: Sequence[str]) -> Iterator[tuple[int, list[str]]]:
    """Yield ``(start_line, content_lines)`` for each ``agent-context`` block."""
    for start, end in _fence_regions(lines):
        info = FENCE_RE.match(lines[start]).group(2).strip()  # type: ignore[union-attr]
        if info.split()[0:1] != ['agent-context']:
            continue
        if end == -1:
            yield start, list(lines[start + 1 :])
        else:
            yield start, list(lines[start + 1 : end])


RUN_COMMAND_RE = re.compile(r"""^-\s*["']Run:\s*(.*?)["']\s*$""")


def find_agent_context_commands(text: str) -> list[str]:
    """Inventory ``Run:`` commands stored in a document, without executing them."""
    commands: list[str] = []
    lines = text.splitlines()
    for _, content in iter_agent_context(lines):
        for line in content:
            match = RUN_COMMAND_RE.match(line.strip())
            if match and match.group(1).strip():
                commands.append(match.group(1).strip())
    return commands


def _scan_agent_context(text: str, rel: Path) -> list[Issue]:
    issues: list[Issue] = []
    lines = text.splitlines()
    for start, content in iter_agent_context(lines):
        if yaml is None:
            continue
        try:
            data = yaml.safe_load('\n'.join(content))
        except yaml.YAMLError as exc:
            issues.append(Issue(
                'CHECK 10',
                str(rel),
                f'agent-context block at line {start + 1} is not valid YAML: {exc}',
            ))
            continue
        if not isinstance(data, dict) or not isinstance(data.get('triggers'), list):
            issues.append(Issue(
                'CHECK 10',
                str(rel),
                f'agent-context block at line {start + 1} has no triggers list',
            ))
    return issues


def scan_content(graph_path: str | os.PathLike[str]) -> list[Issue]:
    """CHECK 10: scan stored documents for containment and hidden characters."""
    root = Path(graph_path)
    issues: list[Issue] = []
    if not root.is_dir():
        return [Issue('CHECK 10', str(root), 'graph path is not a directory')]

    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if 'chats' in rel.parts or 'node_modules' in rel.parts or not path.is_file():
            continue
        if path.suffix.lower() not in {'.md', '.base'}:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(Issue('CHECK 10', str(rel), f'cannot read file: {exc}'))
            continue

        for line, message in _scan_invisible(text):
            issues.append(Issue('CHECK 10', str(rel), f'line {line}: {message}'))

        lines = text.splitlines()
        if path.suffix.lower() == '.md':
            try:
                frontmatter, body = split_frontmatter(text)
            except ValidationError as exc:
                issues.append(Issue('CHECK 10', str(rel), str(exc)))
                body = lines
            else:
                for key in _duplicate_keys(frontmatter):
                    issues.append(
                        Issue('CHECK 10', str(rel), f'duplicate frontmatter key: {key}')
                    )
                for line, message in _scan_leaked_keys(body):
                    issues.append(
                        Issue('CHECK 10', str(rel), f'line {line}: {message}')
                    )
            issues.extend(_scan_agent_context(text, rel))

        for line, message in scan_fences(lines):
            issues.append(Issue('CHECK 10', str(rel), f'line {line}: {message}'))

        if re.match(r'^.+\.graph-(sequence|relationships)\.md$', path.name):
            for index, line in enumerate(lines, start=1):
                if '%%{' in line:
                    issues.append(Issue(
                        'CHECK 10',
                        str(rel),
                        f'line {index}: Mermaid directive in generated diagram',
                    ))

    return issues


# ---------------------------------------------------------------------------
# Graph integrity (VERIFY CHECK 1-8)
# ---------------------------------------------------------------------------

SKIP_DIRS = frozenset({'chats', 'node_modules', '.git', '.obsidian'})
WIKI_LINK_RE = re.compile(r'\[\[([^\[\]|#^]+)(?:[|#^][^\[\]]*)?\]\]')
NODE_FILE_RE = re.compile(
    r'^(?P<project>[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?)\.'
    r'(?P<name>[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?)\.md$'
)
STALE_DAYS = 90

REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    'entity': (
        'type',
        'name',
        'category',
        'importance',
        'status',
        'project',
        'created',
        'updated',
        'agents',
        'tags',
        'related',
        'health',
        'usage',
    ),
    'concept': (
        'type',
        'name',
        'category',
        'importance',
        'status',
        'created',
        'updated',
        'related',
    ),
    'decision': (
        'type',
        'name',
        'title',
        'status',
        'created',
        'updated',
        'related'
    ),
    'constraint': (
        'type',
        'name',
        'category',
        'importance',
        'status',
        'created',
        'updated',
        'related',
    ),
    'process': (
        'type',
        'name',
        'category',
        'importance',
        'status',
        'created',
        'updated',
        'related',
    ),
    'tombstone': (
        'type',
        'name',
        'redirect_to',
        'created'
    ),
}


@dataclass
class Node:
    """A parsed graph document plus the facts the checks need."""

    path: Path
    rel: str
    frontmatter: dict[str, object] | None
    body: str
    error: str | None = None


def _iter_graph_files(
    root: Path, suffixes: tuple[str, ...] = ('.md', '.base')
) -> Iterator[Path]:
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if SKIP_DIRS & set(rel.parts):
            continue
        if path.is_file() and path.suffix.lower() in suffixes:
            yield path


def _load_node(root: Path, path: Path) -> Node:
    rel = str(path.relative_to(root))
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        return Node(path, rel, None, '', f'cannot read file: {exc}')

    if path.suffix.lower() != '.md':
        return Node(path, rel, None, text)

    try:
        frontmatter, body = split_frontmatter(text)
    except ValidationError as exc:
        return Node(path, rel, None, text, str(exc))

    body_text = '\n'.join(body)
    if yaml is None:
        return Node(
            path, rel, None, body_text, 'PyYAML not installed; frontmatter not parsed'
        )
    try:
        data = yaml.safe_load('\n'.join(frontmatter))
    except yaml.YAMLError as exc:
        return Node(path, rel, None, body_text, f'frontmatter is not valid YAML: {exc}')
    if not isinstance(data, dict):
        return Node(path, rel, None, body_text, 'frontmatter is not a mapping')
    return Node(path, rel, data, body_text)


def _related_raw(data: dict[str, object]) -> list[str]:
    """The raw strings stored in ``related``, wiki-link syntax intact."""
    raw = data.get('related')
    if raw is None:
        return []
    if not isinstance(raw, list):
        raw = [raw]
    return [item for item in raw if isinstance(item, str)]


def _related_links(data: dict[str, object]) -> list[str]:
    return [
        match.group(1).strip()
        for item in _related_raw(data)
        for match in WIKI_LINK_RE.finditer(item)
    ]


def _wiki_links(text: str) -> list[str]:
    return [match.group(1).strip() for match in WIKI_LINK_RE.finditer(text)]


class Graph:
    """Index of every node name in the graph, keyed by wiki-link target."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.nodes: dict[str, Node] = {}
        self.by_stem: dict[str, list[Node]] = {}
        self.all: list[Node] = []
        for path in _iter_graph_files(root):
            node = _load_node(root, path)
            self.all.append(node)
            self.by_stem.setdefault(path.stem, []).append(node)
            if node.frontmatter and isinstance(node.frontmatter.get('name'), str):
                self.nodes.setdefault(str(node.frontmatter['name']), node)

    def resolve(self, target: str) -> Node | None:
        if target in self.nodes:
            return self.nodes[target]
        matches = self.by_stem.get(target)
        if matches and len(matches) == 1:
            return matches[0]
        return None

    def project_ids(self) -> set[str]:
        ids: set[str] = set()
        for node in self.all:
            if node.frontmatter and isinstance(node.frontmatter.get('project'), str):
                ids.add(str(node.frontmatter['project']))
            if NODE_FILE_RE.match(node.path.name):
                ids.add(node.path.name.split('.', 1)[0])
        return ids


def check_links(graph: Graph) -> list[Issue]:
    """CHECK 1, CHECK 2 and CHECK 3: links resolve, backlinks reciprocate, no duplicates."""
    issues: list[Issue] = []
    for node in graph.all:
        source = node.body
        if node.frontmatter is not None:
            source = '\n'.join(_related_raw(node.frontmatter)) + '\n' + node.body
        for target in _wiki_links(source):
            if graph.resolve(target) is None:
                issues.append(
                    Issue('CHECK 1', node.rel, f'unresolved wiki-link [[{target}]]')
                )

    for node in graph.all:
        if not node.frontmatter:
            continue
        name = node.frontmatter.get('name')
        if not isinstance(name, str):
            continue
        seen: set[str] = set()
        for target in _related_links(node.frontmatter):
            if target in seen:
                issues.append(
                    Issue('CHECK 3', node.rel, f'duplicate related entry [[{target}]]')
                )
                continue
            seen.add(target)
            other = graph.resolve(target)
            if other is None or not other.frontmatter:
                continue
            if name not in _related_links(other.frontmatter):
                issues.append(Issue(
                    'CHECK 2',
                    node.rel,
                    f'[[{target}]] does not link back to [[{name}]]',
                ))
    return issues


def check_frontmatter(graph: Graph) -> list[Issue]:
    """CHECK 5, CHECK 6 and CHECK 7: required fields, freshness, changelog order."""
    issues: list[Issue] = []
    today = datetime.date.today()
    for node in graph.all:
        if node.frontmatter is None:
            if node.path.suffix.lower() == '.md':
                issues.append(Issue('CHECK 5', node.rel, node.error or 'no readable frontmatter'))
            continue
        data = node.frontmatter
        node_type = data.get('type')
        if not isinstance(node_type, str):
            issues.append(Issue('CHECK 5', node.rel, "missing or non-string 'type'"))
            continue
        required = REQUIRED_FIELDS.get(node_type)
        if required is None:
            issues.append(Issue(
                'CHECK 5',
                node.rel,
                f'unknown node type {node_type!r}',
                severity='warning',
            ))
            continue
        if missing := [field for field in required if field not in data]:
            issues.append(Issue(
                'CHECK 5',
                node.rel,
                'missing required fields: ' + ', '.join(missing),
            ))

        health = data.get('health')
        if node_type == 'entity' and isinstance(health, dict):
            for field in (
                'stale_files',
                'last_verified',
                'needs_update',
                'needs_delete',
            ):
                if field not in health:
                    issues.append(Issue('CHECK 5', node.rel, f'missing health.{field}'))

        updated = _parse_date(data.get('updated'))
        if updated is not None:
            age = (today - updated).days
            if age > STALE_DAYS:
                issues.append(Issue(
                    'CHECK 6',
                    node.rel,
                    f'updated {updated} is {age} days old (> {STALE_DAYS})',
                    severity='warning',
                ))

        changelog = data.get('changelog')
        if isinstance(changelog, list):
            issues.extend(_check_changelog(node.rel, changelog))
    return issues


def _check_changelog(rel: str, entries: Sequence[object]) -> list[Issue]:
    issues: list[Issue] = []
    previous_version: str | None = None
    previous_date = None
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            issues.append(
                Issue('CHECK 7', rel, f'changelog entry {index} is not a mapping')
            )
            continue
        version = entry.get('version')
        if not isinstance(version, str) or not version.strip():
            issues.append(
                Issue('CHECK 7', rel, f'changelog entry {index} has no version')
            )
        elif version == previous_version:
            issues.append(Issue(
                'CHECK 7',
                rel,
                f'duplicate changelog version {version!r} at entry {index}',
            ))
        date = _parse_date(entry.get('date'))
        if date is not None and previous_date is not None and date < previous_date:
            issues.append(Issue(
                'CHECK 7',
                rel,
                f'changelog entry {index} goes back in time ({date} < {previous_date})',
            ))
        if date is not None:
            previous_date = date
        if isinstance(version, str):
            previous_version = version
    return issues


def check_namespace(graph: Graph) -> list[Issue]:
    """CHECK 8: filenames, names and links carry the {project}. prefix."""
    issues: list[Issue] = []
    if not (projects := graph.project_ids()):
        return issues
    project = min(projects)
    prefix = project + '.'

    for node in graph.all:
        if node.path.suffix.lower() != '.md':
            continue
        if not NODE_FILE_RE.match(node.path.name) and not node.path.name.startswith(prefix):
            issues.append(Issue('CHECK 8', node.rel, f'filename missing "{prefix}" prefix'))

    for node in graph.all:
        if not node.frontmatter:
            continue
        name = node.frontmatter.get('name')
        if isinstance(name, str) and '.' not in name:
            issues.append(
                Issue('CHECK 8', node.rel, f'name {name!r} missing "{prefix}" prefix')
            )
        project_field = node.frontmatter.get('project')
        if project_field is not None and project_field != project:
            issues.append(Issue(
                'CHECK 8',
                node.rel,
                f'project {project_field!r} does not match graph project {project!r}',
            ))
        source = '\n'.join(_related_raw(node.frontmatter)) + '\n' + node.body
        for target in _wiki_links(source):
            if '.' not in target:
                issues.append(Issue(
                    'CHECK 8',
                    node.rel,
                    f'wiki-link [[{target}]] missing "{prefix}" prefix',
                ))
    return issues


def check_implementation_files(graph: Graph, codebase: Path | None) -> list[Issue]:
    """CHECK 4: implementation_files exist relative to the codebase root."""
    issues: list[Issue] = []
    base = codebase or Path.cwd()
    for node in graph.all:
        if not node.frontmatter:
            continue
        files = node.frontmatter.get('implementation_files')
        if isinstance(files, str):
            files = [files]
        if not isinstance(files, list):
            continue
        for entry in files:
            if not isinstance(entry, str) or not entry.strip():
                issues.append(Issue(
                    'CHECK 4',
                    node.rel,
                    f'invalid implementation_files entry {entry!r}',
                ))
                continue
            candidate = Path(entry)
            if candidate.is_absolute() or '..' in candidate.parts:
                issues.append(Issue(
                    'CHECK 4',
                    node.rel,
                    f'implementation file escapes the codebase: {entry!r}',
                ))
                continue
            if not (base / candidate).exists():
                issues.append(Issue(
                    'CHECK 4',
                    node.rel,
                    f'implementation file missing: {entry}',
                    severity='warning',
                ))
    return issues


def _parse_date(value: object):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return None


def scan_graph(
    graph_path: str | os.PathLike[str],
    codebase: str | os.PathLike[str] | None = None,
) -> tuple[list[Issue], list[tuple[str, str]]]:
    """Run every mechanical check (CHECK 1-10).

    Returns ``(issues, agent_context_commands)``. ``agent-context`` commands are
    inventoried for the report and never executed.
    """
    root = Path(graph_path)
    issues = scan_paths(root) + scan_content(root)
    commands: list[tuple[str, str]] = []
    if not root.is_dir():
        return issues, commands

    graph = Graph(root)
    issues = (
        issues
        + check_links(graph)
        + check_frontmatter(graph)
        + check_namespace(graph)
        + check_implementation_files(graph, Path(codebase) if codebase else None)
    )

    for path in sorted(root.rglob('*.md')):
        rel = path.relative_to(root)
        if SKIP_DIRS & set(rel.parts):
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        commands.extend(
            (str(rel), command) for command in find_agent_context_commands(text)
        )
    return issues, commands


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


CHECK_TITLES: tuple[tuple[str, str], ...] = (
    ('CHECK 1', 'Wiki-Link Resolution'),
    ('CHECK 2', 'Bidirectional Backlinks'),
    ('CHECK 3', 'Duplicate Related Entries'),
    ('CHECK 4', 'Implementation Files'),
    ('CHECK 5', 'Frontmatter Completeness'),
    ('CHECK 6', 'Updated Date Freshness'),
    ('CHECK 7', 'Changelog Consistency'),
    ('CHECK 8', 'Namespace Conformance'),
    ('CHECK 9', 'Path Safety'),
    ('CHECK 10', 'Content Safety'),
)


def _format_human(issues: Iterable[Issue], commands: Sequence[tuple[str, str]]) -> str:
    issues = list(issues)
    out: list[str] = []
    for check, title in CHECK_TITLES:
        relevant = [issue for issue in issues if issue.check == check]
        out.append(f'{check}: {title} ' + '-' * 30)
        if not relevant:
            out.append('PASS')
        else:
            out.extend(
                f'{issue.severity.upper()}: {issue.path}: {issue.message}'
                for issue in relevant
            )
        out.append('')
    if commands:
        out.append('agent-context Run: entries (not executed)')
        out.extend(f'  {path}: {command}' for path, command in commands)
        out.append('')
    errors = sum(1 for issue in issues if issue.severity == 'error')
    warnings = len(issues) - errors
    out.append(f'Summary: {errors} error(s), {warnings} warning(s)')
    return '\n'.join(out)


def _summarize(issues: Iterable[Issue]) -> list[dict[str, object]]:
    """One row per check, for machine-readable reports."""
    issues = list(issues)
    rows: list[dict[str, object]] = []
    for check, title in CHECK_TITLES:
        relevant = [issue for issue in issues if issue.check == check]
        rows.append(
            {
                'check': check,
                'title': title,
                'status': 'FAIL' if relevant else 'PASS',
                'issues': len(relevant),
            }
        )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Validate a knowledge-graph directory (VERIFY CHECK 1-10).'
    )
    parser.add_argument('graph_path', help='path to {vault}/{memory}/{project}')
    parser.add_argument(
        '--json', action='store_true', help='emit machine-readable JSON'
    )
    parser.add_argument(
        '--strict', action='store_true', help='treat warnings as failures'
    )
    parser.add_argument(
        '--codebase',
        help='project root used to resolve implementation_files (CHECK 4); defaults to the current directory',
    )
    args = parser.parse_args(argv)

    if not Path(args.graph_path).is_dir():
        print(f'error: not a directory: {args.graph_path}', file=sys.stderr)
        return 2

    issues, commands = scan_graph(args.graph_path, args.codebase)
    errors = [issue for issue in issues if issue.severity == 'error']
    warnings = [issue for issue in issues if issue.severity == 'warning']
    failed = bool(errors) or (args.strict and bool(warnings))

    if args.json:
        print(
            json.dumps(
                {
                    'graph_path': str(Path(args.graph_path)),
                    'codebase': str(Path(args.codebase)) if args.codebase else str(Path.cwd()),
                    'issues': [asdict(issue) for issue in issues],
                    'agent_context_commands': [
                        {'path': path, 'command': command} for path, command in commands
                    ],
                    'errors': len(errors),
                    'warnings': len(warnings),
                    'ok': not failed,
                    'checks': _summarize(issues),
                },
                indent=2,
            )
        )
    else:
        print(_format_human(issues, commands))

    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
