# 4. Generic validation framework

**Status: needs design discussion before coding.**

## Problem

Consumers need to validate rules against their domain schema: "does this path exist? is this field writable? is this literal assignable to this field? does this workflow accept these args?" Vectrix-backend's `rule_validation.py` (522 lines) does this with regex-based identifier extraction and a bespoke field catalog.

## Constraint

Rulang should **not** define a schema format. Consumers have different schema systems (typed dicts, Pydantic, domain registries, nothing at all). Imposing one shape would make rulang less generic.

## Proposal

A visitor-based validation framework. Rulang walks the AST; the consumer answers domain questions via a `Resolver` protocol.

### Sketch

```python
from rulang import validate, Resolver, Diagnostic

class MyResolver(Resolver):
    def check_path(self, path: Path) -> PathInfo | Unknown: ...
    def check_literal(self, path: Path, literal: Literal) -> Ok | TypeMismatch: ...
    def check_workflow(self, name: str, args: list[Expr]) -> Ok | Unknown | ArgMismatch: ...

diagnostics: list[Diagnostic] = validate(rule, MyResolver())
```

Rulang owns:
- AST traversal
- Literal type inference
- Path reconstruction for error messages
- Diagnostic formatting (message, pointer into source, severity)
- Collecting all diagnostics (not failing fast)

Consumer owns:
- Schema shape and lookup logic
- Semantic rules specific to their domain (enum value forms, scope restrictions)

### Diagnostic shape (sketch)

```python
Diagnostic {
    severity: "error" | "warning" | "info"
    code: str                # e.g. "unknown_path", "type_mismatch"
    message: str
    span: Span | None        # source position, if available
    related: list[Diagnostic]
}
```

## Open questions (discuss before implementing)

1. **How prescriptive should the `Resolver` interface be?** Structural (Python `Protocol` / TS interface) with optional hooks the consumer can leave unimplemented, or a formal ABC?
2. **Should we ship an opt-in `DictSchemaResolver` convenience** for the common case of a flat `{path: type}` schema, or keep rulang 100% BYO?
3. **Diagnostic codes**: do we standardize a fixed set now, or let consumers extend?
4. **Async resolvers**: needed, or sync-only for v1?
5. **Partial validation**: can a consumer validate only paths and skip workflow checks? How does the API signal "not my problem, don't complain"?
6. **Source spans**: do we need them in proposal #1 first, or can validation diagnostics reconstruct positions from the AST alone?

## Non-goals

- No built-in schema format.
- No type inference beyond literals (won't infer types of `PathRef` expressions without a resolver).
- No autofix suggestions in v1.
