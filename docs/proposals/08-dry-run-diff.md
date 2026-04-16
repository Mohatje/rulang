# 8. Dry-run diff API

## Problem

Consumers that preview, test, or debug rules (e.g., vectrix-backend's `dry_runner.py` and `rule_tester.py`, ~900 lines combined) re-implement "evaluate against a sample entity and show me what changed" on top of `RuleEngine.evaluate`. They deep-copy entities, track before/after states manually, and reconstruct which conditions matched.

## Proposal

A first-class dry-run API on `RuleEngine` that returns a structured result instead of just the final value.

### API

```python
result = engine.dry_run(entity, workflows=None, *, deep_copy=True)
```

TS: `engine.dryRun(entity, { workflows?, deepCopy? })`.

### `DryRunResult` shape

```python
DryRunResult {
    matched_rules: list[MatchedRule]
    executed_actions: list[ExecutedAction]   # in execution order
    diff: dict[Path, tuple[Before, After]]   # aggregated field-level changes
    final_entity: Entity                     # post-run snapshot
    returned: Any | None                     # value evaluate() would have returned
}

MatchedRule {
    index: int
    rule_text: str
    condition_result: bool
    condition_trace: list[ConditionStep]     # which sub-conditions matched
    executed: bool                           # False for matched-but-skipped (first_match losers)
}

ExecutedAction {
    rule_index: int
    action: Action
    path: Path
    before: Any
    after: Any
}
```

### Mode behavior

- **all_match**: traces every rule in dependency order; `matched_rules` includes both matched and unmatched; `executed_actions` lists every applied action.
- **first_match**: traces all rules up to and including the first match; rules whose conditions were evaluated but lost to an earlier match appear with `executed=False` so UIs can show "would have matched, but rule #3 won."

### Non-mutation

`deep_copy=True` (default) runs against a copy — callers can safely dry-run the same entity repeatedly. `deep_copy=False` for perf-sensitive cases where the caller handles copying.

### Consumer use cases this unblocks

- Rule preview UIs ("this rule would set `priority` from `normal` to `high`").
- Regression tests for rule sets ("applying this rule to these 50 fixtures should produce these diffs").
- Debugging ("which condition in this compound expression was false?").
- Impact analysis for rule changes.

## Non-goals

- No test-row generation (that's domain-specific — consumers build fixtures).
- No assertion DSL — just return the data; let consumers assert however they want.
- No UI rendering.

## Open questions

- How detailed should `condition_trace` be? Full sub-expression evaluation tree, or just top-level and/or branches? Start minimal and expand based on consumer feedback.
- Do we expose `condition_trace` for non-matched rules too (so UIs can show *why* a rule didn't match)? Probably yes — that's a big debugging win and the cost is small once we're already tracing.
