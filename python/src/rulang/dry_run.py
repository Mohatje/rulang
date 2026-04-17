"""
Dry-run diff API (proposal #8).

`RuleEngine.dry_run()` evaluates rules against an entity and returns a
structured trace instead of just the final value. Intended for previewing,
debugging, and regression-testing rule changes.

The returned `DryRunResult` exposes:

- `matched_rules`: every rule with its condition result and whether it
  executed. In first_match mode, rules that matched but lost to an earlier
  rule appear with `executed=False` so UIs can surface them.
- `executed_actions`: ordered list of actions that ran, with per-path
  before/after values.
- `diff`: aggregated path → (before, after) across the whole run.
- `final_entity`: post-run entity snapshot.
- `returned`: the value `evaluate()` would have returned.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class MatchedRule:
    index: int
    rule_text: str
    condition_result: bool
    executed: bool


@dataclass(frozen=True)
class ActionChange:
    """A single path-level change produced by an action."""

    path: str
    before: Any
    after: Any


@dataclass(frozen=True)
class ExecutedAction:
    """One action's trace: which rule it came from and what it changed."""

    rule_index: int
    action_kind: Literal["set", "compound", "workflow", "return"]
    changes: tuple[ActionChange, ...]
    returned: Any = None  # set only when action_kind == "return"


@dataclass(frozen=True)
class DryRunResult:
    matched_rules: tuple[MatchedRule, ...]
    executed_actions: tuple[ExecutedAction, ...]
    diff: dict[str, tuple[Any, Any]]
    final_entity: Any
    returned: Any

    @property
    def any_matched(self) -> bool:
        return any(m.executed for m in self.matched_rules)


# --- Entity diffing -----------------------------------------------------


def _diff_entities(before: Any, after: Any, path: str = "") -> dict[str, tuple[Any, Any]]:
    """Return {path: (before_value, after_value)} for paths that differ."""
    if _same(before, after):
        return {}

    # If types differ or either is a leaf, record the whole node.
    if type(before) is not type(after):
        return {path or "<root>": (before, after)}

    if isinstance(before, dict):
        changes: dict[str, tuple[Any, Any]] = {}
        keys = set(before.keys()) | set(after.keys())
        for k in keys:
            sub_path = f"{path}.{k}" if path else str(k)
            if k not in before:
                changes[sub_path] = (None, after[k])
            elif k not in after:
                changes[sub_path] = (before[k], None)
            else:
                changes.update(_diff_entities(before[k], after[k], sub_path))
        return changes

    if isinstance(before, list):
        if len(before) != len(after):
            return {path or "<root>": (before, after)}
        changes = {}
        for i, (b, a) in enumerate(zip(before, after)):
            sub_path = f"{path}[{i}]"
            changes.update(_diff_entities(b, a, sub_path))
        return changes

    # Objects with __dict__
    if hasattr(before, "__dict__") and hasattr(after, "__dict__"):
        changes = {}
        keys = set(vars(before).keys()) | set(vars(after).keys())
        for k in keys:
            sub_path = f"{path}.{k}" if path else str(k)
            b = getattr(before, k, None)
            a = getattr(after, k, None)
            changes.update(_diff_entities(b, a, sub_path))
        return changes

    # Leaf scalars
    return {path or "<root>": (before, after)}


def _same(a: Any, b: Any) -> bool:
    try:
        return a == b
    except Exception:  # noqa: BLE001
        return a is b
