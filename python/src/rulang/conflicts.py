"""
Conflict detection for rule sets (proposal #5).

Built on the public AST (proposal #1) and the canonical formatter
(proposal #3). `detect_conflicts` returns a list of structured `Conflict`
objects:

- `duplicate`: two rules with identical canonical condition AND actions.
- `contradiction`: identical canonical condition, at least one common
  write path, different literal values at that path.
- `shadowing` (first_match mode only): two rules with identical canonical
  conditions where the earlier would always win, making the later one
  unreachable.

v1 is purely syntactic — based on canonical-form equality and direct
literal comparison. Semantic implication (e.g. `x > 100` implies `x > 50`)
is out of scope and documented as a v2 extension in proposal #5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Union

from rulang.ast import (
    Compound,
    Literal_,
    Rule,
    Set_,
    parse,
)
from rulang.formatter import format_action, format_condition, format_path

ConflictKind = Literal["duplicate", "contradiction", "shadowing"]


@dataclass(frozen=True)
class Conflict:
    """A detected conflict between two rules.

    `rule_indices` holds the indices of the conflicting rules in the input
    list. `fields` names the write paths involved (for contradictions and
    some duplicates). `diff` maps field → tuple of literal values when the
    conflict is a contradiction; empty otherwise.
    """

    kind: ConflictKind
    rule_indices: tuple[int, int]
    fields: tuple[str, ...]
    diff: dict[str, tuple[Any, Any]]
    message: str


def detect_conflicts(
    rules: list[Union[str, Rule]],
    mode: Literal["first_match", "all_match"] = "all_match",
    entity_name: str = "entity",
) -> list[Conflict]:
    """
    Detect duplicate, contradictory, and shadowing rules.

    Args:
        rules: a list of rule source strings or `Rule` ASTs (mixed is fine).
        mode: match the engine mode you're targeting. `shadowing` is only
            reported in `first_match` — in `all_match`, two rules with
            identical conditions and different actions are complementary,
            not shadowing.
        entity_name: used when parsing string rules.

    Returns:
        A list of `Conflict` objects. Pairs are reported in input order and
        a pair can contribute at most one entry (duplicate supersedes
        contradiction and shadowing).
    """
    asts: list[Rule] = [r if isinstance(r, Rule) else parse(r, entity_name=entity_name) for r in rules]

    metas = [_analyze(ast) for ast in asts]

    conflicts: list[Conflict] = []
    for i in range(len(asts)):
        for j in range(i + 1, len(asts)):
            m1, m2 = metas[i], metas[j]

            if m1.condition_canon != m2.condition_canon:
                continue

            # Duplicate — identical canonical condition + identical action set
            if m1.actions_canon == m2.actions_canon:
                conflicts.append(
                    Conflict(
                        kind="duplicate",
                        rule_indices=(i, j),
                        fields=tuple(sorted(m1.write_paths)),
                        diff={},
                        message=f"Rules {i} and {j} are identical after normalization.",
                    )
                )
                continue

            # Contradiction — same condition, common write path, different literal
            shared_literal_paths = (
                set(m1.literal_writes.keys()) & set(m2.literal_writes.keys())
            )
            diff_fields = [
                p
                for p in shared_literal_paths
                if m1.literal_writes[p] != m2.literal_writes[p]
            ]
            if diff_fields:
                conflicts.append(
                    Conflict(
                        kind="contradiction",
                        rule_indices=(i, j),
                        fields=tuple(sorted(diff_fields)),
                        diff={
                            p: (m1.literal_writes[p], m2.literal_writes[p])
                            for p in diff_fields
                        },
                        message=(
                            f"Rules {i} and {j} have identical conditions but write "
                            f"different literal values to: {', '.join(sorted(diff_fields))}."
                        ),
                    )
                )
                continue

            # Shadowing — first_match only, identical conditions, non-duplicate actions
            if mode == "first_match":
                conflicts.append(
                    Conflict(
                        kind="shadowing",
                        rule_indices=(i, j),
                        fields=(),
                        diff={},
                        message=(
                            f"Rule {j} is unreachable in first_match mode: "
                            f"rule {i} has an identical condition and runs first."
                        ),
                    )
                )

    return conflicts


@dataclass(frozen=True)
class _RuleMeta:
    condition_canon: str
    actions_canon: frozenset[str]
    write_paths: frozenset[str]
    literal_writes: dict[str, Any]


def _analyze(rule: Rule) -> _RuleMeta:
    """Compute comparison-ready canonical strings and literal-write map."""
    condition_canon = format_condition(rule.condition)
    actions_canon = frozenset(format_action(a) for a in rule.actions)
    write_paths: set[str] = set()
    literal_writes: dict[str, Any] = {}
    for action in rule.actions:
        if isinstance(action, (Set_, Compound)):
            path_str = format_path(action.path)
            write_paths.add(path_str)
            if isinstance(action, Set_) and isinstance(action.value, Literal_):
                literal_writes[path_str] = (action.value.type, action.value.value)
    return _RuleMeta(
        condition_canon=condition_canon,
        actions_canon=actions_canon,
        write_paths=frozenset(write_paths),
        literal_writes=literal_writes,
    )
