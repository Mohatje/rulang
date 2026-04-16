# 2. Builder-support primitives

## Problem

Consumers building visual rule builders (node graphs, form UIs) need to go both directions: rule text → structured nodes, and structured nodes → rule text. Without support, they write regex splitters and hand-rolled literal formatters, and they can't trust round-trips.

## Research finding

We should **not** ship a visual-graph shape — that's product-specific. A consumer's nodes, edges, and layout model belong to their UI. The right rulang-level primitive is the AST (proposal #1) plus ergonomic construction helpers plus a round-trip guarantee via the formatter (proposal #3).

## Proposal

### Ergonomic constructors

So clients never hand-assemble rule strings:

```python
from rulang import Rule, Condition as C, Action as A, Path

rule = Rule.of(
    condition=C.and_(
        C.eq(Path.of("shipment", "weight"), 100),
        C.exists(Path.of("shipment", "customer_pk")),
    ),
    actions=[
        A.set(Path.of("shipment", "priority"), "high"),
    ],
)

text = rulang.format(rule)
```

TS mirrors with identical naming conventions (camelCase).

### Round-trip contract

Enforced by spec tests:

- `parse(format(ast))` is structurally equal to `ast`.
- `format(parse(text))` is the canonical form of `text` (proposal #3).
- `format(parse(format(ast)))` equals `format(ast)` (idempotence).

### Consumer workflow

Forward (rule text → UI):
1. `parse(text) → Rule`
2. Walk AST, emit consumer's node-graph shape.

Reverse (UI edits → rule text):
1. Consumer constructs AST via `Rule.of(…)`, `Condition.eq(…)`, etc.
2. `format(rule) → text`.

This removes every regex and ad-hoc literal formatter from consumer code.

## Non-goals

- No node/graph/diagram types in rulang.
- No UI concerns (positioning, colors, labels).
- No opinion about how a builder UI groups conditions visually.

## Open questions

- A future `rulang-builder` companion package could offer a framework-agnostic graph model if multiple consumers converge on similar needs. Not in scope here.
