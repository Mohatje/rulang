# rulang (Python)

Python implementation of the [Rulang](https://github.com/Mohatje/rulang) business-rules DSL. Semantic parity with the TypeScript runtime is enforced by a shared spec suite.

## Install

```bash
uv add rulang
```

## Quick start

```python
from rulang import RuleEngine

engine = RuleEngine(mode="all_match")
engine.add_rules([
    "entity.age >= 18 => entity.is_adult = true",
    "entity.is_adult == true => entity.discount += 0.1",
])

entity = {"age": 25, "is_adult": False, "discount": 0.0}
engine.evaluate(entity)
# entity is now {'age': 25, 'is_adult': True, 'discount': 0.1}
```

The full DSL (operators, paths, built-in functions, null-safe access) is documented in the top-level [README](../README.md) and in the runtime-shipped reference (`rulang.grammar_reference()`).

## Tooling API at a glance

- `rulang.parse(text)` — returns a public AST with source spans on every node.
- `rulang.walk(node, visitor)` — pre-order AST traversal.
- `rulang.format(rule)` — canonical string form. Idempotent; round-trips through `parse`. Companion helpers: `format_condition`, `format_action`, `format_path`, `format_expr`.
- `rulang.detect_conflicts(rules, mode=…)` — duplicate/contradiction/shadowing findings across a rule set.
- `engine.dry_run(entity)` — structured trace with per-action before/after, aggregated diff, final entity, and return value.
- `rulang.validate(rule, resolver, severity_overrides=…)` — list of `Diagnostic`. Schema-agnostic; consumers subclass `BaseResolver` and override hooks. Parse errors are returned as diagnostics — `validate` never raises.
- `rulang.builders` — ergonomic AST constructors: `rule`, comparisons (`eq`, `neq`, `lt`, `gt`, `lte`, `gte`, `in_`, `not_in`, `contains`, `startswith`, `endswith`, `matches`, `contains_any`, `contains_all`), logical (`and_`, `or_`, `not_`), existence (`exists`, `is_empty`), actions (`set_`, `compound`, `workflow_call`, `ret`), and `pathref`/`lit`/`float_lit`/`int_lit`/`fn`/`binary`/`unary`/`null_coalesce`/`workflow_expr`.
- `rulang.grammar_reference()` — canonical LLM-ready grammar cheatsheet (markdown), versioned with the package.

For worked examples of each feature, see the top-level [README's "Tooling API" section](../README.md#tooling-api).

## Diagnostic codes

`rulang.validation.DIAGNOSTIC_CODES` lists every rulang-owned code. Consumer diagnostics should use their own namespace (e.g. `myapp.*`). Defaults and overrides are documented in the [root README](../README.md#diagnostic-codes).

## Repository layout

- `src/rulang/` — source
- `tests/` — Python-specific tests
- `tests/spec/` — cross-runtime spec runners; fixtures live in `../spec/cases/` and `../spec/feature-cases/`
- `../grammar/BusinessRules.g4` — shared ANTLR grammar (source of truth)
- `../docs/proposals/` — design proposals for each capability

## Development

```bash
# Dev install
uv sync --all-extras

# Run tests with coverage
uv run pytest tests/

# Regenerate parsers after grammar edits (run from repo root)
cd .. && npm run generate:parsers
```

## License

MIT
