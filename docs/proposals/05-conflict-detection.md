# 5. Conflict detection

## Problem

Consumers need to know when a set of rules contains duplicates, contradictions, or shadowed rules. Vectrix-backend's `conflict_detector.py` (400 lines) does this with regex-based signature parsing and path-prefix stripping — work that would be nearly trivial given a real AST and canonical form.

## Proposal

Built on proposal #1 (AST) and proposal #3 (canonical formatter).

### API

```python
from rulang import detect_conflicts, Conflict

conflicts: list[Conflict] = detect_conflicts(rules, mode="all_match")
```

Accepts rules as text or `Rule` AST nodes. `mode` matches `RuleEngine.mode`.

### Conflict kinds (v1)

- **Duplicate**: identical canonical condition + identical canonical actions.
- **Contradiction**: identical canonical condition; at least one write path in common; different literal values at that path.
- **Shadowing** (first-match mode only): rule *A* appears before rule *B*; their canonical conditions are identical; *B* is unreachable.

### Conflict shape

```python
Conflict {
    kind: "duplicate" | "contradiction" | "shadowing"
    rule_indices: list[int]
    fields: list[Path]        # involved write paths
    diff: dict[Path, list[Literal]]   # for contradictions
    message: str              # human-readable summary
}
```

Consumer renders however it wants (CLI output, UI badges, PR comments).

### v2+ ideas (not in initial scope)

- Condition implication (rule A's condition logically implies rule B's): requires a small satisfiability engine for the condition algebra.
- Numeric range overlap (e.g., `weight > 100` vs. `weight > 50`).
- Enum set overlap (`status in ['a', 'b']` vs. `status == 'a'`).
- Coverage gaps (conditions that leave a field unset in reachable cases).

## Non-goals

- No semantic understanding of domain fields (that's the validation framework's job).
- No autofix / merge suggestions.

## Open questions

- Should `detect_conflicts` require a `Resolver` (proposal #4) to do smarter semantic checks, or keep it purely syntactic in v1 and layer semantic checks on later?
- How do we represent conflicts involving expressions (non-literal RHS) — skip them in v1?
