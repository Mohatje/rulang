# 3. Canonical pretty-printer

## Problem

Consumers doing rule comparison, deduplication, or conflict detection normalize rule text with ad-hoc regex (strip whitespace, rewrite path prefixes, guess quote style). Rulang itself has no canonical string form, so `==` on rule text isn't meaningful.

## Proposal

Ship `rulang.format(rule | ast | text) → str` producing a single canonical form.

### Canonical choices (v1 defaults, not configurable)

- Whitespace: single spaces around operators; one space after commas; no trailing whitespace.
- Strings: always single-quoted, with `\'` for embedded quotes.
- Booleans / null: lowercase `true`, `false`, `none`.
- Numeric literals: integers without trailing `.0`; floats with at least one decimal.
- Operators: pick one spelling where aliases exist (e.g., prefer `!=` over `<>`).
- Parentheses: only where precedence requires.
- Action separator: `; ` between actions.
- `=>` with a single space each side.

### API

```python
rulang.format(text_or_rule) → str
```

Overloads accept:
- raw rule text (parsed then formatted)
- a `Rule` AST node from proposal #1
- a builder result from proposal #2

### Guarantees

- Idempotent: `format(format(x)) == format(x)`.
- Round-trips: `parse(format(ast))` is structurally equal to `ast`.

## Non-goals

- No style options in v1. One canonical form is the point.
- No multiline/verbose mode (possible v2 if the agent UI wants it).

## Enables

- Proposal #5 (conflict detection) uses canonical string equality as a cheap dedup primitive.
- Consumers can store canonical rule text and compare with `==`.
