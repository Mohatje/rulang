"""
Grammar reference accessor (proposal #7).

Rulang ships its canonical grammar reference as package data. Consumers that
prompt LLMs to write rulang (or anyone who wants a versioned reference
guaranteed to match the runtime) should use `grammar_reference()` rather than
hand-maintaining a cheatsheet.
"""

from __future__ import annotations

import importlib.resources as _resources


def grammar_reference() -> str:
    """
    Return the canonical rulang grammar reference as markdown.

    The reference ships with the package and is versioned alongside it, so
    pinning rulang pins the reference.
    """
    return (
        _resources.files("rulang.docs")
        .joinpath("grammar-reference.md")
        .read_text(encoding="utf-8")
    )
