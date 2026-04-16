# Rulang proposals

Forward-looking design proposals for capabilities rulang should own. Motivated by capabilities currently being reimplemented in consumer projects (notably vectrix-backend's business rules agent).

## Index

| # | Proposal | Status |
|---|---|---|
| 1 | [Public AST + extractor APIs](01-public-ast.md) | Shipped |
| 2 | [Builder-support primitives](02-builder-primitives.md) | Shipped |
| 3 | [Canonical pretty-printer](03-canonical-formatter.md) | Shipped |
| 4 | [Generic validation framework](04-validation-framework.md) | Shipped |
| 5 | [Conflict detection](05-conflict-detection.md) | Shipped |
| 6 | [Scope / path resolution](06-scope-resolution-deferred.md) | Deferred |
| 7 | [Grammar reference / rulang skill](07-grammar-reference.md) | Shipped |
| 8 | [Dry-run diff API](08-dry-run-diff.md) | Shipped |

## Suggested build order

1 → 3 → 7 → 8 → 5 → 2 → 4

Rationale: 1 unblocks everything else; 3 is small and unblocks 5; 7 and 8 are independent quick wins; 5 falls out cheaply once 1+3 exist; 2 is mostly ergonomics on top of 1+3; 4 needs a design conversation before coding.
