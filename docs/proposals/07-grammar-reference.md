# 7. Grammar reference / rulang skill

## Problem

Consumers that prompt LLMs to write rulang (e.g., vectrix-backend's business rules agent) hand-maintain a grammar cheatsheet as a giant string constant in their system prompt. It drifts from the real grammar, and every consumer rebuilds the same reference.

## Proposal

Ship a canonical grammar reference as part of the package, queryable at runtime.

### Artifact

`docs/grammar-reference.md` — a markdown document covering:

- Rule structure (`condition => actions [; ret expr]`)
- Operators: comparison, logical, string, existence, null operators
- Built-in functions (grouped: strings, collections, type coercion, math, type checks)
- Path access: dots, indexing (incl. negative), null-safe `?.`, null coalescing `??`
- Literals: strings, numbers, booleans, null, lists
- Assignment forms: `=`, `+=`, `-=`, `*=`, `/=`
- Workflow calls
- Worked examples for each major feature

Tuned to be directly droppable into an LLM system prompt: declarative, concise, example-heavy, minimal prose.

### Packaging

- **Python**: bundled as package data; accessed via `importlib.resources`.
- **TypeScript**: bundled as an asset shipped with the package; accessed via a module import.

### API

```python
import rulang
prompt_fragment: str = rulang.grammar_reference()
```

TS mirror: `rulang.grammarReference()`.

One canonical version ships with each rulang release; consumers pin rulang and get a matching reference automatically.

### Keep-in-sync strategy

Two tests enforce that the reference doesn't drift from the real grammar:

1. **Examples parse**: every rule example block in the markdown is extracted and parsed; the test fails if any example is invalid rulang.
2. **Operator/function coverage**: a single source-of-truth list (either generated from the grammar or a central registry consumed by both the parser and the docs) is compared against the operator/function tables in the markdown. Missing or extra entries fail the test.

### Optional: multiple variants

If useful, ship two variants:

- `grammar_reference()` — full human-readable reference.
- `grammar_reference(style="prompt")` — stripped-down LLM-optimized version.

Decide during implementation based on whether the full doc is already prompt-friendly.

## Non-goals

- Not a tutorial or conceptual guide — this is a reference.
- Not versioned separately from the package.

## Open questions

- Do we also ship a JSON/structured form of the operator+function registry, so consumers can build custom prompts or autocompletes? Probably yes as a follow-up, not in v1.
