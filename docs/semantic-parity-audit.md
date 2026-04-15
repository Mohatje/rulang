# Semantic Parity Audit

This file records the current disposition of the Python test inventory against the semantic parity plan.

Statuses:

- `Shared export`: covered by the generated portable corpus in `spec/generated/python-portable-cases.json`
- `Shared manual`: covered by hand-maintained shared corpora in `spec/portable/*.json`
- `Excluded`: intentionally outside the JSON-like runtime parity domain and tracked in [`semantic-parity-exclusions.json`](./semantic-parity-exclusions.json)
- `Infra`: test infrastructure, not a Python semantic-runtime delta to reconcile

## Python Test File Status

| File | Status | Notes |
| --- | --- | --- |
| `python/tests/test_builtin_functions.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_dependency_graph.py` | Shared manual | Covered by `dependency-graph-portable-cases.json` and related runtime semantics cases. |
| `python/tests/test_dependency_graph_expanded.py` | Shared manual | Deterministic ordering, wildcard overlap, and cycle cases are in shared portable corpora. |
| `python/tests/test_engine.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_engine_edge_cases.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_engine_expanded.py` | Shared manual | JSON-like engine behaviors are covered by shared corpora including `engine-audit-portable-cases.json`; host-object and scale-only cases are excluded. |
| `python/tests/test_engine_runtime_compat.py` | Shared manual | Covered by `engine-sequence-portable-cases.json`. |
| `python/tests/test_existence_operators.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_feature_integration.py` | Shared manual | JSON-like feature interactions are covered by `feature-integration-portable-cases.json`; no remaining promotable cases identified. |
| `python/tests/test_implicit_entity.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_integration.py` | Shared manual | JSON-like business scenarios are covered by `integration-portable-cases.json`; performance-only cases are excluded. |
| `python/tests/test_list_operators.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_null_safe.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_parser.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_parser_edge_cases.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_parser_expanded.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_path_resolver.py` | Shared manual | Covered by `path-resolver-portable-cases.json`. |
| `python/tests/test_path_resolver_edge_cases.py` | Shared manual | JSON-like resolver cases are shared; host-object path behavior is excluded. |
| `python/tests/test_readme_examples.py` | Shared manual | Semantically useful examples are covered by `readme-portable-cases.json` and other shared corpora; duplicates were intentionally not repeated. |
| `python/tests/test_string_operators.py` | Shared export | Covered by generated portable cases. |
| `python/tests/test_visitor.py` | Shared manual | Covered by generated export plus manual interpreter and workflow corpora. |
| `python/tests/test_visitor_edge_cases.py` | Shared manual | JSON-like visitor edge cases are covered by `interpreter-edge-portable-cases.json`, `visitor-closure-portable-cases.json`, and related shared corpora; host-object, callable-arity, and non-JSON collection cases are excluded. |
| `python/tests/test_visitor_expanded.py` | Shared manual | Expanded interpreter semantics are covered across `interpreter-semantics-portable-cases.json`, `interpreter-edge-portable-cases.json`, `visitor-closure-portable-cases.json`, and integration corpora. |
| `python/tests/test_workflows.py` | Excluded | Primarily workflow registry/decorator/package API behavior; tracked by `workflow-registry-api-shape`. |
| `python/tests/test_workflows_expanded.py` | Excluded | Primarily workflow registry/decorator/package API behavior; tracked by `workflow-registry-api-shape`. |
| `python/tests/parity/test_portable_cases.py` | Infra | Python-side parity harness. |
| `python/tests/spec/test_shared_spec.py` | Infra | Shared spec verification, not a Python-vs-TS semantic delta. |

## Remaining Explicitly Local Areas

- Host-object path resolution and assignment semantics
- Workflow registry and decorator API shape
- Host-language callable arity behavior
- Non-JSON host values such as sets, tuples, and similar collection semantics
- Performance and scale-only scenarios

## Release Readiness Interpretation

For the JSON-like parity domain, the remaining work is no longer broad semantic migration. It is release review:

- verify the exclusion register remains intentionally short
- verify no new runtime divergence appears as shared cases are added
- decide whether any excluded behavior must be promoted before release
