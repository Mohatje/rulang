# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-17

### Added

- **Public AST with source spans** (`rulang.parse`, `walk`, plus the full
  node hierarchy: `Rule`, `Condition` variants, `Expr` variants, `Action`
  variants, `Path`). Every AST node carries a `Span` with character offsets
  and line/column so downstream diagnostics can point into source text.
- **Canonical formatter** (`rulang.format`, plus `format_condition`,
  `format_action`, `format_path`, `format_expr`). Produces a single
  canonical string form (stable whitespace, single-quoted strings,
  normalized booleans, canonical operator spellings); idempotent; round-
  trips with `parse`.
- **Conflict detection** (`detect_conflicts`, `Conflict`). Surfaces
  duplicates, literal-value contradictions, and first-match shadowing
  across a rule set using AST + canonical-form equality.
- **Dry-run diff API** (`RuleEngine.dry_run`, `DryRunResult`,
  `ExecutedAction`, `MatchedRule`, `ActionChange`). Evaluates rules
  non-mutatively (deep-copies by default) and returns a structured trace:
  which rules matched, which executed, per-action before/after, an
  aggregated path-level diff, and the return value.
- **Generic validation framework** (`validate`, `BaseResolver`, `Resolver`,
  `Diagnostic`, `PathInfo`, `OK`, `UNKNOWN`). Walks the AST and invokes
  semantic hooks on a user-supplied resolver; never throws (parse errors
  become `rulang.syntax_error` diagnostics); namespaced codes under
  `rulang.*`; per-code `severity_overrides`.
- **Programmatic rule builders** (`rulang.builders`). Ergonomic
  constructors for paths, literals, expressions, conditions, and actions,
  plus `rule()` to compose the final AST. Round-trips through
  `format`/`parse`. Raw strings in expression position are rejected as
  ambiguous; use `pathref(...)` or `lit(...)`.
- **Explicit literal helpers** `float_lit()` / `int_lit()` for
  cross-runtime parity when the Python value is ambiguous (e.g.
  `float_lit(3)` vs. `lit(3)`).
- **Grammar reference** (`grammar_reference()`). Ships the canonical
  LLM-ready grammar cheatsheet as package data; versioned with the runtime
  so consumers can pin.
- **Cross-runtime shared spec** under `spec/feature-cases/` exercising
  `format`, `detect_conflicts`, and `dry_run` against the same fixtures in
  Python and TypeScript.
- **Property-based round-trip tests** — 400 seeded random rules assert
  `format(parse(format(ast))) == format(ast)` in both runtimes.

### Changed

- `RuleEngine.dry_run` is a new method; `evaluate` unchanged.

### Fixed

- N/A (all additions).

## [0.1.0] - 2025-01-10

### Added

- Core rule engine with DSL for business rules evaluation
- ANTLR4-based parser for rule syntax
- Dependency graph analysis with cycle detection
- Path resolution for nested entity access with null-safe operators (`?.`, `?[]`)
- Workflow support with decorator-based registration
- Comprehensive operators:
  - Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
  - Logical: `AND`, `OR`, `NOT`
  - String: `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `MATCHES`
  - Existence: `EXISTS`, `NOT EXISTS`, `IS NULL`, `IS NOT NULL`, `IS EMPTY`, `IS NOT EMPTY`
  - List: `IN`, `NOT IN`, `ALL IN`, `ANY IN`, `NONE IN`
- Built-in functions for strings, collections, type coercion, and math
- Custom exception hierarchy for error handling
