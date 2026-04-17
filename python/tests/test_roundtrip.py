"""Randomized round-trip tests for the formatter.

Builds many random valid Rule ASTs via builders, then asserts:

- format(ast) produces a string
- parse(format(ast)) succeeds
- format(parse(format(ast))) == format(ast)  (idempotence)

We seed the RNG per test so failures are reproducible without adding
hypothesis as a dependency.
"""

from __future__ import annotations

import random
from typing import Any

import pytest

from rulang import format, parse
from rulang.ast import Literal_
from rulang.builders import (
    and_,
    binary,
    compound,
    contains,
    contains_all,
    contains_any,
    endswith,
    eq,
    exists,
    fn,
    gt,
    gte,
    in_,
    is_empty,
    lit,
    lt,
    lte,
    matches,
    neq,
    not_,
    not_contains,
    not_in,
    null_coalesce,
    or_,
    path_of,
    pathref,
    ret,
    rule,
    set_,
    startswith,
    unary,
    workflow_call,
    workflow_expr,
)


# --- Generators ---------------------------------------------------------


_ROOTS = ["entity"]
_FIELDS = ["a", "b", "c", "x", "y", "z", "count", "name", "status", "age", "items", "user"]
_FUNCTIONS = ["lower", "upper", "trim", "len", "first", "last", "abs"]
_WORKFLOWS = ["notify", "log", "score"]


def _rand_path(rng: random.Random, max_depth: int = 3) -> Any:
    segs = [rng.choice(_ROOTS)]
    depth = rng.randint(1, max_depth)
    for _ in range(depth):
        if rng.random() < 0.1:
            segs.append("?." + rng.choice(_FIELDS))
        else:
            segs.append(rng.choice(_FIELDS))
    return path_of(*segs)


def _rand_literal(rng: random.Random) -> Literal_:
    choice = rng.randint(0, 5)
    if choice == 0:
        return lit(rng.randint(-100, 100))
    if choice == 1:
        return lit(round(rng.uniform(-100, 100), 2))
    if choice == 2:
        return lit(rng.choice([True, False]))
    if choice == 3:
        return lit(None)
    if choice == 4:
        return lit(rng.choice(["hello", "world", "foo", "bar", ""]))
    # List
    size = rng.randint(0, 3)
    return lit([_rand_literal(rng) for _ in range(size)])


def _rand_simple_expr(rng: random.Random) -> Any:
    """Keep expressions shallow to avoid runaway recursion."""
    choice = rng.randint(0, 3)
    if choice == 0:
        return _rand_literal(rng)
    if choice == 1:
        return pathref(_rand_path(rng))
    if choice == 2:
        name = rng.choice(_FUNCTIONS)
        return fn(name, _rand_literal(rng))
    # Binary on two simple operands
    a = pathref(_rand_path(rng))
    b = _rand_literal(rng)
    if isinstance(b, Literal_) and b.type in ("int", "float"):
        op = rng.choice(["+", "-", "*"])
        return binary(a, op, b)
    return a


def _rand_comparison(rng: random.Random) -> Any:
    builders_list = [eq, neq, lt, gt, lte, gte]
    op = rng.choice(builders_list)
    left = pathref(_rand_path(rng))
    right = _rand_literal(rng)
    # Some ops work best with specific operand types; filter unsafe combos
    if op in (lt, gt, lte, gte) and isinstance(right, Literal_) and right.type not in ("int", "float", "string"):
        right = lit(rng.randint(0, 100))
    return op(left, right)


def _rand_string_op(rng: random.Random) -> Any:
    ops = [contains, not_contains, startswith, endswith, matches]
    op = rng.choice(ops)
    return op(pathref(_rand_path(rng)), lit(rng.choice(["a", "hello", "prefix", "suffix"])))


def _rand_list_op(rng: random.Random) -> Any:
    ops = [in_, not_in, contains_any, contains_all]
    op = rng.choice(ops)
    return op(pathref(_rand_path(rng)), lit([rng.randint(1, 10) for _ in range(rng.randint(1, 3))]))


def _rand_existence(rng: random.Random) -> Any:
    op = rng.choice([exists, is_empty])
    return op(pathref(_rand_path(rng)))


def _rand_condition_leaf(rng: random.Random) -> Any:
    picks = [
        _rand_comparison,
        _rand_string_op,
        _rand_list_op,
        _rand_existence,
    ]
    return rng.choice(picks)(rng)


def _rand_condition(rng: random.Random, depth: int = 0, max_depth: int = 3) -> Any:
    if depth >= max_depth or rng.random() < 0.4:
        return _rand_condition_leaf(rng)
    choice = rng.randint(0, 3)
    if choice == 0:
        return and_(
            _rand_condition(rng, depth + 1, max_depth),
            _rand_condition(rng, depth + 1, max_depth),
        )
    if choice == 1:
        return or_(
            _rand_condition(rng, depth + 1, max_depth),
            _rand_condition(rng, depth + 1, max_depth),
        )
    if choice == 2:
        return not_(_rand_condition(rng, depth + 1, max_depth))
    return _rand_condition_leaf(rng)


def _rand_action(rng: random.Random) -> Any:
    choice = rng.randint(0, 3)
    if choice == 0:
        return set_(_rand_path(rng), _rand_literal(rng))
    if choice == 1:
        op = rng.choice(["+=", "-=", "*=", "/="])
        return compound(_rand_path(rng), op, lit(rng.randint(1, 10)))
    if choice == 2:
        name = rng.choice(_WORKFLOWS)
        if rng.random() < 0.5:
            return workflow_call(name)
        return workflow_call(name, _rand_literal(rng))
    return ret(_rand_literal(rng))


def _rand_rule(rng: random.Random) -> Any:
    cond = _rand_condition(rng)
    action_count = rng.randint(1, 3)
    actions = [_rand_action(rng) for _ in range(action_count)]
    return rule(cond, actions)


# --- Invariants --------------------------------------------------------


SEEDS = list(range(200))


@pytest.mark.parametrize("seed", SEEDS)
def test_random_rule_round_trips(seed):
    rng = random.Random(seed)
    try:
        r = _rand_rule(rng)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"generator produced invalid input for seed {seed}: {exc}")

    # format() must produce a string
    text = format(r)
    assert isinstance(text, str)

    # parse must succeed
    reparsed = parse(text)
    assert reparsed is not None

    # format(parse(format(ast))) must equal format(ast)
    round_tripped = format(reparsed)
    assert round_tripped == text, (
        f"round trip failed for seed {seed}: {text!r} -> {round_tripped!r}"
    )


@pytest.mark.parametrize("seed", SEEDS)
def test_format_idempotent_under_random_inputs(seed):
    rng = random.Random(seed)
    try:
        r = _rand_rule(rng)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"generator produced invalid input for seed {seed}: {exc}")

    once = format(r)
    twice = format(parse(once))
    assert once == twice
