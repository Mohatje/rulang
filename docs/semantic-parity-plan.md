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

## Python Test Inventory and Required Action

Every Python test file should land in one of three buckets:

- `Portable now`: already represented in shared parity cases
- `Promote`: convert to shared parity cases
- `Keep local with reason`: runtime-local behavior that is intentionally out of scope

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

### Promote Next

- `test_dependency_graph.py`
  - promote dependency edge construction
  - promote execution order
  - promote cycle detection and cycle breaking
  - promote workflow-driven dependency edges
- `test_dependency_graph_expanded.py`
  - promote deterministic ordering
  - promote wildcard path overlap behavior
  - promote larger cycle and dependency scenarios
- `test_engine_expanded.py`
  - promote expanded engine behaviors not already covered by exported cases
  - promote multi-step mutation and return scenarios
  - promote workflow ordering scenarios
- `test_engine_runtime_compat.py`
  - promote workflow dependency cache invalidation after prior inspection
- `test_feature_integration.py`
  - promote combined-feature mutation flows
  - promote mixed operator interactions that affect writes
- `test_integration.py`
  - promote end-to-end business scenarios that are purely JSON-like
- `test_path_resolver.py`
  - promote path resolution and assignment behavior for portable inputs
- `test_path_resolver_edge_cases.py`
  - promote path resolution edge cases for portable inputs
  - split out Python object-specific cases into runtime-local coverage if needed
- `test_visitor.py`
  - promote interpreter-level semantics not already covered through `RuleEngine`
- `test_visitor_edge_cases.py`
  - promote edge cases for operators, functions, and failure behavior
- `test_visitor_expanded.py`
  - promote expanded interpreter semantics that affect return values or writes
- `test_workflows.py`
  - promote workflow semantics
  - promote registry and wrapper semantics where portable
- `test_workflows_expanded.py`
  - promote expanded workflow argument and metadata behavior

### Keep Local With Reason

These should remain local unless the parity domain is expanded:

- Python dataclass-specific path resolution
- Python property and bound-method resolution
- TypeScript-only host object behavior such as `Map`, `Set`, and `Date`
- decorator syntax differences at the host-language API level

If any of these influence real user rule outcomes on supported payloads, remove them from this section and promote them.

## Harness Gaps To Close

The current portable harness primarily supports three case kinds:

- `evaluate`
- `parse`
- `parse_error`

That is not enough to cover the whole semantic surface. Add these portable case kinds:

- `resolve`
  - input entity
  - `entity_name`
  - path parts
  - null-safe indices
  - expected value or error category
- `assign`
  - input entity
  - `entity_name`
  - path parts
  - assigned value
  - expected final entity or error category
- `dependency_graph`
  - rules
  - optional workflows with metadata
  - expected graph edges
  - expected execution order
  - expected cycles if relevant
- `evaluate_error`
  - rules
  - input entity
  - optional workflows
  - expected error category

Without these case kinds, parity will remain weaker than the Python semantic surface.

## Conversion Strategy

Use this order.

### Phase 1. Freeze the Contract

- keep this document up to date
- create an exclusion register file once the first intentional exclusions exist
- treat undocumented divergence as a release blocker

### Phase 2. Expand the Harness

- extend the JSON parity schema to support `resolve`, `assign`, `dependency_graph`, and `evaluate_error`
- add Python and TypeScript runners for each new case kind
- make the parity suite print the exact failing dimension: parse, analysis, order, return, mutation, or error

### Phase 3. Promote Path and Graph Semantics

- convert `test_path_resolver.py`
- convert portable parts of `test_path_resolver_edge_cases.py`
- convert `test_dependency_graph.py`
- convert `test_dependency_graph_expanded.py`
- convert `test_engine_runtime_compat.py`

This phase closes the highest leverage gap for mutation correctness because order and path semantics directly change writes.

### Phase 4. Promote Interpreter and Workflow Semantics

- convert `test_visitor.py`
- convert `test_visitor_edge_cases.py`
- convert `test_visitor_expanded.py`
- convert `test_workflows.py`
- convert `test_workflows_expanded.py`
- convert remaining portable cases from `test_engine_expanded.py`

### Phase 5. Promote Integration Scenarios

- convert JSON-like cases from `test_feature_integration.py`
- convert JSON-like cases from `test_integration.py`
- convert portable examples from `test_readme_examples.py`

Keep example formatting and documentation checks local if they do not add semantic value.

### Phase 6. Close the Remaining Gaps

- audit every Python test file line by line
- mark each test as:
  - already portable
  - newly portable
  - intentionally local
- fail the release if any semantic test remains unclassified

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
