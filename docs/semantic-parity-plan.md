# Semantic Parity Plan

This document defines the release bar for the TypeScript runtime.

The target is not package-level API parity. The target is semantic parity:

- Given the same supported rules
- Given the same supported input entity
- Given the same evaluation mode
- Given the same workflow metadata and workflow behavior

Python and TypeScript must:

- accept or reject the same rule text
- compute the same read/write/workflow analysis
- execute rules in the same order
- return the same value
- mutate the entity in the same way
- fail in the same category when evaluation is invalid

## Supported Parity Domain

The parity domain for release should be explicit:

- JSON-like entities: objects/dicts, arrays/lists, strings, numbers, booleans, null/None
- nested object/list paths
- workflow calls with explicit read/write metadata
- rule strings supported by the shared grammar in [`grammar/BusinessRules.g4`](../grammar/BusinessRules.g4)

The following are runtime-local unless explicitly promoted into the parity domain:

- Python dataclass behavior
- Python object property and method resolution
- JavaScript class instance behavior
- JavaScript `Map`, `Set`, and `Date` behavior
- package API shape differences between Python and TypeScript
- exact exception message text

If any runtime-local behavior can affect rule matching or entity mutation for real user data, it must be promoted into the parity domain and tested in both runtimes.

## Release Gate

Do not release the TypeScript runtime as semantically equivalent unless all of the following are true:

- Every semantic Python test is either:
  - represented in a shared parity case, or
  - listed in an explicit exclusion register with a reason.
- The parity suite compares:
  - parse acceptance/rejection
  - read set
  - write set
  - workflow call set
  - execution order
  - return value
  - final entity mutation
  - error category
  - preserved prior mutations for shared post-error cases
- There are no known semantic divergences that are not documented.
- The exclusion register is intentionally short and reviewed before release.

## Current Coverage

The current portable export in [`python/tools/export_portable_cases.py`](../python/tools/export_portable_cases.py) covers these Python test files:

- `test_builtin_functions.py`
- `test_engine.py`
- `test_engine_edge_cases.py`
- `test_existence_operators.py`
- `test_implicit_entity.py`
- `test_list_operators.py`
- `test_null_safe.py`
- `test_parser.py`
- `test_parser_edge_cases.py`
- `test_parser_expanded.py`
- `test_string_operators.py`

That is a strong start, but it is not the full semantic surface. The remaining Python-only files still contain behavior that can change rule matching, execution order, or mutations.

## Current Status Snapshot

The parity program has moved beyond the original exported subset.

Implemented shared portable corpora now cover:

- parser and syntax behavior from the generated Python export
- path resolution and assignment behavior for JSON-like entities
- dependency graph construction, deterministic ordering, and cycle cases
- workflow-driven ordering and cache invalidation after prior inspection
- interpreter semantics including return flow, compound assignment, arithmetic, truthiness, null coalescing, and workflow invocation
- feature-integration and end-to-end integration scenarios for JSON-like entities
- selected README examples that add semantic coverage rather than duplicate existing cases
- deterministic error-state assertions, including preserved prior mutations after failure

The harness now supports and exercises these case kinds in both runtimes:

- `evaluate`
- `parse`
- `parse_error`
- `resolve`
- `assign`
- `dependency_graph`
- `evaluate_error`
- `engine_sequence`

The file-by-file audit is complete and recorded in
[`semantic-parity-audit.md`](./semantic-parity-audit.md).

Remaining work is now release review rather than semantic migration:

- keep the exclusion register intentionally short and explicit
- verify new shared cases do not introduce undocumented divergence
- decide whether any excluded behavior must be promoted before release

## Entire Semantic Surface

The parity program must cover all of the following.

### 1. Grammar and Parsing

- keywords: `true`, `false`, `none`, `null`, `and`, `or`, `not`, `in`, `not in`, `ret`, `workflow`
- operators: `==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `%`, `=`, `+=`, `-=`, `*=`, `/=`
- extended operators: `contains`, `not contains`, `startswith`, `starts_with`, `endswith`, `ends_with`, `matches`, `contains_any`, `contains_all`, `exists`, `is_empty`, `isempty`
- delimiters: `=>`, `;`, `(`, `)`, `[`, `]`, `.`, `?.`, `??`, `,`
- literals: strings, escapes, integers, floats, booleans, null/None, lists
- whitespace and comments
- precedence and associativity
- syntax failures and tokenization failures

### 2. Static Analysis

- `reads`
- `writes`
- `workflow_calls`
- path normalization for implicit entity access
- wildcard path analysis for indexed paths

### 3. Path Resolution

- explicit entity root
- implicit entity root
- nested object/dict access
- list indexing
- negative list indexing
- null-safe traversal
- missing path errors
- assignment path resolution

### 4. Evaluation Semantics

- `and`, `or`, `not`
- short-circuit behavior
- return semantics
- action sequencing
- first-match mode
- all-match mode

### 5. Nullish and Emptiness Semantics

- `exists`
- `is_empty`
- `isempty`
- `?.`
- `??`
- preservation of `0`, `false`, `""`, `[]`, and `{}`

### 6. Comparison and Membership Semantics

- equality and inequality
- list any-satisfies semantics
- list-vs-list exact equality
- numeric ordering
- string ordering where supported
- `in`
- `not in`
- string operators
- regex behavior for valid and invalid patterns
- `contains_any`
- `contains_all`

### 7. Built-in Functions

- `lower`
- `upper`
- `trim`
- `strip`
- `int`
- `float`
- `str`
- `bool`
- `len`
- `first`
- `last`
- `keys`
- `values`
- `abs`
- `round`
- `min`
- `max`
- `is_list`
- `is_string`
- `is_number`
- `is_none`

### 8. Mutation Semantics

- direct assignment
- compound assignment on numbers
- compound assignment on strings
- compound assignment on lists
- nested assignment
- list element assignment

### 9. Workflow Semantics

- plain workflow calls
- wrapped workflow calls
- nested workflow calls
- workflow return values
- workflow argument evaluation
- workflow registry behavior
- workflow dependency metadata

### 10. Dependency Analysis and Ordering

- dependency graph edge construction
- workflow-driven dependencies
- topological ordering
- deterministic ordering
- cycle detection
- cycle breaking
- cache correctness after prior graph inspection

### 11. Error Semantics

- parse errors
- path resolution errors
- missing workflow errors
- evaluation errors from unsupported operations
- preserved prior mutations before failure in ordered shared cases

## Python Test Inventory and Required Action

Every Python test file should land in one of three buckets:

- `Portable now`: already represented in shared parity cases
- `Promote`: convert to shared parity cases
- `Keep local with reason`: runtime-local behavior that is intentionally out of scope

The current file-by-file audit lives in [`semantic-parity-audit.md`](./semantic-parity-audit.md).

### Already Portable

- `test_builtin_functions.py`
- `test_engine.py`
- `test_engine_edge_cases.py`
- `test_existence_operators.py`
- `test_implicit_entity.py`
- `test_list_operators.py`
- `test_null_safe.py`
- `test_parser.py`
- `test_parser_edge_cases.py`
- `test_parser_expanded.py`
- `test_string_operators.py`

### Audit Outcome

- The original “Promote Next” files have now been audited.
- JSON-like semantics from those files are either represented in shared parity cases or explicitly covered by the exclusion register.
- Remaining non-shared items are primarily host-language API behavior, non-JSON host values, or performance-only checks.

### Keep Local With Reason

These should remain local unless the parity domain is expanded:

- Python dataclass-specific path resolution
- Python property and bound-method resolution
- TypeScript-only host object behavior such as `Map`, `Set`, and `Date`
- decorator syntax differences at the host-language API level

If any of these influence real user rule outcomes on supported payloads, remove them from this section and promote them.

## Harness Gaps To Close

These gaps are closed. The portable harness now supports:

- `resolve`
- `assign`
- `dependency_graph`
- `evaluate_error`
- `engine_sequence`

The harness and audit coverage are in place. The remaining gap is release
decision-making around the explicit exclusions.

## Conversion Strategy

Use this order.

### Phase 1. Freeze the Contract

- keep this document up to date
- create an exclusion register file once the first intentional exclusions exist
- treat undocumented divergence as a release blocker

### Phase 2. Expand the Harness

- completed
- the JSON parity schema and both runtime runners support `resolve`, `assign`, `dependency_graph`, `evaluate_error`, and `engine_sequence`
- the suite now distinguishes parse, analysis, ordering, return-value, mutation, and error failures

### Phase 3. Promote Path and Graph Semantics

- completed for the JSON-like parity domain
- shared corpora cover portable path resolution, assignment, dependency graphs, ordering, cycle handling, and cache invalidation after prior inspection

This phase closes the highest leverage gap for mutation correctness because order and path semantics directly change writes.

### Phase 4. Promote Interpreter and Workflow Semantics

- completed for the JSON-like parity domain
- shared corpora cover interpreter semantics, return flow, workflow invocation, truthiness, null coalescing, failure behavior, and closure cases
- workflow registry and package-shape tests remain intentionally local and are tracked in the exclusion register

### Phase 5. Promote Integration Scenarios

- completed for the JSON-like parity domain
- JSON-like cases from feature integration, integration, and README examples have been promoted where they add semantic value

Keep example formatting and documentation checks local if they do not add semantic value.

### Phase 6. Close the Remaining Gaps

- completed
- every Python semantic test file is now classified in the audit as shared, excluded, or infrastructure
- any future semantic test added on the Python side should be treated as a release blocker until it is either shared or explicitly excluded

## Test Conversion Rules

When moving a Python test into parity:

- prefer converting the original scenario instead of inventing a simpler one
- keep the case JSON-like unless the parity domain explicitly includes richer host objects
- preserve the exact mutation assertions
- preserve the exact return-value assertion
- preserve ordering assertions when the test depends on ordering
- preserve error-category assertions for negative tests
- preserve the workflow metadata exactly

If a Python test cannot be represented by the current portable format, extend the format instead of dropping the case.

## Exclusion Register Template

When an intentional divergence exists, record it in a machine-readable file with:

- `id`
- `area`
- `behavior`
- `python_behavior`
- `typescript_behavior`
- `reason`
- `risk`
- `owner`
- `review_by_release`

There should be very few of these.

The current exclusion register lives in [`semantic-parity-exclusions.json`](./semantic-parity-exclusions.json).

## Definition of Done

The TypeScript runtime is ready to release as semantically equivalent when:

- this document is satisfied
- the shared parity suite covers the entire supported semantic surface
- every Python semantic test is either shared or explicitly excluded
- there are no undocumented divergences affecting rule matching, ordering, return values, or mutations
