# 1. Public AST + extractor APIs

## Problem

Rulang's parse tree and `RuleAnalyzer` are internal. Consumers that need to inspect rules (for validation, conflict detection, visual builders, impact analysis, etc.) fall back to regex: splitting on `=>`, on `and`/`or`, pulling out identifiers. This is fragile and drifts from the real grammar.

## Proposal

Promote the parse tree to a stable, documented public AST of pure data types — not the ANTLR tree.

### Node types (sketch)

- `Rule { condition: Condition, actions: list[Action], ret: Expr | None }`
- `Condition`:
  - `And(left, right)`, `Or(left, right)`, `Not(inner)`
  - `Comparison(left: Expr, op: CompOp, right: Expr)`
  - `Existence(path, kind: "exists" | "is_empty")`
  - `StringOp(path, op, arg)` (`contains`, `startswith`, `endswith`, `matches`, `contains_any`, `contains_all`)
- `Action`:
  - `Set(path, expr)`, `Compound(path, op, expr)` (`+=`, `-=`, …)
  - `WorkflowCall(name, args)`
- `Expr`: `Literal`, `PathRef`, `FunctionCall`, `BinaryOp`, `NullCoalesce`
- `Literal { value, type: "string" | "int" | "float" | "bool" | "none" | "list" }` (type inferred at parse time)
- `Path { segments: list[PathSegment] }` with segments for fields, indices, null-safe access

### Source spans

Every AST node carries a `Span` with source position info:

```
Span {
    start: int        # character offset, inclusive
    end: int          # character offset, exclusive
    line: int         # 1-based
    column: int       # 1-based, at start
}
```

Spans are populated at parse time from the underlying ANTLR position info — cheap to collect, and we want them on every node so downstream features (validation diagnostics in proposal #4, editor integration, error highlighting) can point into source without approximation.

Spans are also preserved through the ergonomic constructors in proposal #2 where feasible (programmatically-built ASTs may have `None` spans — consumers should treat spans as optional at the type level).

### API

- `rulang.parse(text: str) → Rule` returning the public AST.
- On `Rule`: `.reads`, `.writes`, `.workflow_calls`, `.conditions`, `.actions`, `.literals`.
- `rulang.walk(node, visitor)` helper for custom AST traversal.
- TS mirror with identical shape and field names.

### Internals

Rewire the interpreter, `RuleAnalyzer`, and the dependency graph to consume this public AST — so the public surface stays honest and can't drift from what the engine actually uses.

## Parity

Both Python and TS expose the same node shapes and field names. Shared spec suite asserts parity: same input → same AST structure.

## Non-goals

- No AST mutation helpers in v1 — construction goes through the builders in proposal #2.

## Open questions

- Dataclasses (Python) / interfaces (TS) vs. richer classes with methods? Leaning toward pure data + free functions for easy serialization.
- Do we version the AST shape independently of the package version?
- Span representation: bare character offsets only, or include line/column as shown? Line/column is convenient for diagnostics but redundant with offsets + source text. Leaning toward shipping both since the cost is small.
