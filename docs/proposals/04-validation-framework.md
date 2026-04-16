# 4. Generic validation framework

**Status: design agreed. Ready to implement.**

## Problem

Consumers need to validate rules against their domain schema: "does this path exist? is this field writable? is this literal assignable to this field? does this workflow accept these args?" Vectrix-backend's `rule_validation.py` (522 lines) does this with regex-based identifier extraction and a bespoke field catalog.

## Constraint

Rulang must not define a schema format. Consumers have different schema systems (typed dicts, Pydantic, domain registries, nothing at all). Imposing one shape would make rulang less generic.

## Design

A visitor-based validation framework. Rulang walks the AST; the consumer answers domain questions via a `Resolver` protocol. Rulang owns AST traversal, literal type inference, and diagnostic formatting. Consumer owns schema shape, lookup, and domain semantics.

### Resolver interface

**Shape: Protocol + `BaseResolver` with no-op defaults.** Consumers subclass `BaseResolver` and override only the hooks they care about. Unimplemented hooks return `Unknown`, which rulang treats as "skip — consumer opted out of this check." No diagnostic emitted for opted-out hooks.

```python
from rulang.validation import BaseResolver, Ok, Unknown, Diagnostic
from rulang.ast import Path, Expr, PathInfo

class MyResolver(BaseResolver):
    def check_path(self, path: Path) -> PathInfo | Unknown:
        # "does this path exist, is it writable, what's its type"
        ...

    def check_assignment(self, path: Path, value: Expr) -> Ok | list[Diagnostic]:
        # "can this expression be assigned to this path"
        # receives the full value expression, not just literals
        ...

    def check_comparison(self, left: Expr, op: CompOp, right: Expr) -> Ok | list[Diagnostic]:
        # "are these two expressions type-comparable under this operator"
        ...

    def check_workflow_call(self, name: str, args: list[Expr]) -> Ok | list[Diagnostic]:
        # "does this workflow exist, are these args valid"
        ...
```

TS mirrors with identical method names in camelCase (`checkPath`, `checkAssignment`, etc.).

### Hook granularity — semantic, not per-node

Hooks operate on **semantic actions** (assignments, comparisons, workflow calls) rather than individual AST nodes. Hooks receive full expression ASTs — not pre-reduced to literals — so consumers can reason about arbitrary RHS expressions (`shipment.weight * 2`, `lower(trim(x))`, etc.).

**Key implication**: rulang is not a typechecker. It doesn't infer types of `PathRef` or `FunctionCall` expressions — the consumer's resolver is the only party that knows path types, so type reasoning on expressions is the consumer's job. Rulang's contribution is literal type inference (already done at parse time) plus AST traversal and diagnostic plumbing.

Hooks return `Ok`, `Unknown`, or `list[Diagnostic]`. Consumers can emit diagnostics rulang wouldn't have asked about (e.g., "this sets a deprecated field"), making the hooks the extension point for all semantic checks — not just the ones rulang named.

### `validate()` — always returns, never raises

```python
from rulang import validate

diagnostics: list[Diagnostic] = validate(
    rule_text_or_ast,
    resolver,
    severity_overrides={"rulang.unknown_path": "warning"},  # optional
)
```

**Returns**, never raises. `validate()` is meant for rule-creation flows where authoring is iterative and a hard error would disrupt UX. The caller decides what severity means crash vs. warn.

Rulang only raises for genuine programmer errors (e.g., `resolver` is not a `Resolver`). Rule syntax errors are surfaced as diagnostics, not exceptions — see "Parse errors" below.

### Parse errors are diagnostics

When `validate()` is called with raw rule text, parse errors appear in the returned diagnostics with code `rulang.syntax_error`. This keeps the consumer's mental model single: one list to display, covering both "syntax invalid" and "unknown path." No branching on parse-succeeded vs. parse-failed before validation can run.

If parsing fails, `validate()` returns the parse diagnostics and stops — downstream semantic checks can't run on an unparsed rule.

### Diagnostic shape

```python
Diagnostic {
    severity: "error" | "warning" | "info"
    code: str                          # namespaced, e.g. "rulang.unknown_path"
    message: str
    span: Span | None                  # source position from proposal #1
    related: list[Diagnostic]          # optional supplementary diagnostics
}
```

### Diagnostic codes — namespaced strings

Rulang owns a fixed set of codes for what rulang detects; consumers namespace their own:

**Rulang-owned (stable across versions):**
- `rulang.syntax_error` — parse failed
- `rulang.unknown_path` — resolver returned Unknown for a path; severity depends on caller config
- `rulang.type_mismatch` — resolver flagged an assignment/comparison type problem
- `rulang.unknown_workflow` — resolver flagged workflow call
- `rulang.workflow_arg_mismatch` — resolver flagged arg shape
- `rulang.invalid_literal` — literal couldn't be parsed/typed

**Consumer-owned:** any string starting with a non-`rulang.` namespace, e.g., `myapp.enum_value_must_be_stored_form`.

Rulang assigns default severities to its own codes (e.g., `rulang.unknown_path` → error). Consumers downgrade or upgrade via `severity_overrides`. Consumer-owned codes carry whatever severity the resolver set.

### Severity handling

- Rulang's own codes have built-in default severities.
- Resolver-returned diagnostics carry whatever severity the resolver chose.
- `severity_overrides={code: severity}` on `validate()` applies last, overriding both defaults and resolver choices. Intended for per-project customization ("in this repo, unknown paths are warnings, not errors").

### Sync-only in v1

No `validate_async`. If a resolver needs DB-backed lookups, cache into memory before calling `validate`. We'll add an async variant if real demand surfaces — adding it later is non-breaking.

### No built-in schema resolver in v1

We intentionally don't ship a `DictSchemaResolver` or `FlatPathResolver` convenience. The point of this proposal is rulang stays schema-agnostic; shipping any default schema shape sends the opposite signal and becomes the de facto standard. If multiple consumers reimplement the same starter resolver, we'll ship it in v1.1 with that evidence in hand.

## Scope boundaries

**In scope for #4:**
- Per-rule validation
- Path existence, type, writability
- Assignment and comparison semantic checks
- Workflow call checks
- Consumer-extensible diagnostics

**Out of scope — belongs elsewhere:**
- Multi-rule / cross-rule analysis (duplicates, contradictions, shadowing) → proposal #5
- Dependency-order checks → existing dependency graph
- Full expression-level type inference → resolver's responsibility, not rulang's
- Autofix / suggestion generation → future proposal if demand exists

## Dependency

Requires source spans on AST nodes (proposal #1). Diagnostics without spans are noticeably worse UX and retrofitting spans later would break the AST shape.

## Rollout

1. Land proposal #1 first (public AST with spans).
2. Ship `Resolver` protocol + `BaseResolver` + `Diagnostic` + `validate()` in both runtimes.
3. Document the rulang-owned diagnostic code set as part of the public API surface.
4. Shared spec tests cover: every resolver hook, no-op defaults behavior, severity overrides, parse errors as diagnostics, consumer-emitted diagnostics.
