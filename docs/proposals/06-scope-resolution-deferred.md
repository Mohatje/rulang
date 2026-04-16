# 6. Scope / path resolution — deferred

**Status: deferred. Recommend leaving in consumer-land.**

## Summary

Vectrix-backend's `rule_field_registry.py` maintains per-scope field path tables (`SHIPMENT_FIELD_PATHS`, `GOODS_LINE_FIELD_PATHS`, `STOP_FIELD_PATHS`) and resolves bare names like `weight` to different paths depending on which entity the rule targets. Initial framing suggested rulang should own this.

## Why it stays in consumer-land

On closer look, what's being called "scopes" is actually **multi-entity selection plus short-name rewriting** — a domain model concern:

- Vectrix has multiple entity types (shipment, goods_line, stop) and picks a root based on what's being rule-applied.
- Bare `weight` means different things depending on which entity is the root — that's an application-level ergonomic, not a DSL concept.
- Rulang's contract is "evaluate one rule against one entity." It has no model of which entity, or why a name should rewrite.

The piece that *is* generic — resolving dotted paths within a single entity — is already handled by `PathResolver`.

## What rulang provides today that's sufficient

- `PathResolver` handles within-entity access including dicts, objects, dataclasses, indexing, null-safe paths.
- Rules that need short names can simply be written against the entity structure the consumer passes in.

## When to revisit

If a second consumer surfaces a similar need — multiple entity types with contextual name rewriting — we'd have evidence that the pattern is generic enough to promote. Until then, keeping this out of rulang avoids baking vectrix's domain model into the DSL.

## Not closing the door

If we later identify a *DSL-level* primitive here (e.g., a standard way to declare aliases within a rule, or a cross-entity reference syntax), we can open a new proposal. This one is deferred, not rejected.
