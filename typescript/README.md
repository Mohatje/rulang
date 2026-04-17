# @mohatje/rulang

TypeScript runtime for the [Rulang](https://github.com/Mohatje/rulang) business-rules DSL. Semantic parity with the Python reference implementation is enforced by a shared spec suite.

## Install

```bash
npm install @mohatje/rulang
```

## Quick start

```ts
import { RuleEngine } from "@mohatje/rulang";

const engine = new RuleEngine("all_match");
engine.addRules([
  "entity.age >= 18 => entity.isAdult = true",
  "entity.isAdult == true => entity.discount += 0.1",
]);

const entity = { age: 25, isAdult: false, discount: 0 };
engine.evaluate(entity);
// entity is now { age: 25, isAdult: true, discount: 0.1 }
```

The full DSL — operators, paths, built-in functions, null-safe access — is documented in the top-level [README](https://github.com/Mohatje/rulang#readme) and in the runtime-shipped reference (`grammarReference()`).

## Tooling API

Beyond the engine, the package exposes cross-runtime tooling APIs for consumers that build rule editors, linters, LLM agents, or validation pipelines.

### Public AST

```ts
import { parse, walk } from "@mohatje/rulang";

const rule = parse("entity.age >= 18 => entity.adult = true");
rule.reads;        // Set { "entity.age" }
rule.writes;       // Set { "entity.adult" }
rule.condition;    // { type: "comparison", ... }
rule.actions;      // [ { type: "set", ... } ]

walk(rule, (node) => console.log(node.type));
```

Every AST node carries a `span: { start, end, line, column }` so downstream diagnostics can point back into source.

### Canonical formatter

```ts
import { format } from "@mohatje/rulang";
format("entity.x==1=>entity.y=2");   // "entity.x == 1 => entity.y = 2"
```

Idempotent and round-trips through `parse`. Companion helpers: `formatCondition`, `formatAction`, `formatPath`, `formatExpr`.

### Conflict detection

```ts
import { detectConflicts } from "@mohatje/rulang";

detectConflicts([
  "entity.x == 1 => entity.y = 'a'",
  "entity.x == 1 => entity.y = 'b'",
]);
// [ { kind: "contradiction", ruleIndices: [0, 1], fields: ["entity.y"], diff: {...}, message: "..." } ]
```

Detects `duplicate`, `contradiction`, and (in `first_match` mode) `shadowing` across a rule set.

### Dry-run with diff

```ts
const engine = new RuleEngine("all_match");
engine.addRules([
  "entity.a == 0 => entity.a = 1",
  "entity.a == 1 => entity.b = 2",
]);

const result = engine.dryRun({ a: 0, b: 0 });
result.diff;           // { a: [0, 1], b: [0, 2] }
result.finalEntity;    // { a: 1, b: 2 }
result.matchedRules;   // per-rule condition + executed flags
result.returned;       // true
```

Deep-copies the entity by default — call `engine.dryRun(entity, { deepCopy: false })` to opt out.

### Generic validation

```ts
import { BaseResolver, validate, type Path, type PathInfo } from "@mohatje/rulang";

class SchemaResolver extends BaseResolver {
  static KNOWN = new Set(["entity.age", "entity.adult"]);
  override checkPath(path: Path): PathInfo {
    return { exists: SchemaResolver.KNOWN.has(path.root + "." + path.segments.map((s) => ("name" in s ? s.name : "[*]")).join(".")) };
  }
}

validate("entity.missing >= 18 => entity.adult = true", new SchemaResolver());
// [ { code: "rulang.unknown_path", severity: "error", message: "...", span: { ... } } ]
```

Hooks: `checkPath`, `checkAssignment`, `checkComparison`, `checkWorkflowCall`. Unimplemented hooks return `UNKNOWN`/`OK` and emit no diagnostic. Parse errors are returned as `rulang.syntax_error` diagnostics — `validate` never throws.

See [Diagnostic codes](https://github.com/Mohatje/rulang#diagnostic-codes) in the root README for the full list of rulang-owned codes.

### Programmatic rule building

```ts
import { builders, format } from "@mohatje/rulang";
const { rule, eq, and, pathref, lit, set_ } = builders;

const r = rule(
  and(
    eq(pathref("entity.status"), lit("active")),
    eq(pathref("entity.verified"), true),
  ),
  [set_("entity.canOrder", true)],
);

format(r);
// "entity.status == 'active' and entity.verified == true => entity.canOrder = true"
```

Raw strings in expression position are rejected (ambiguous — could mean a path or a literal); use `pathref("entity.x")` or `lit("x")`. For explicit float-vs-int literals use `builders.floatLit(3)` / `builders.intLit(3)`.

### Grammar reference

```ts
import { grammarReference } from "@mohatje/rulang";
const prompt = grammarReference();  // canonical LLM-ready cheatsheet (markdown)
```

Ships with the package and is versioned alongside it — pinning the rulang version pins the reference.

## Naming conventions vs. Python

The TypeScript API mirrors Python with two mechanical adaptations. A rough cheat sheet:

| Python                  | TypeScript               |
|-------------------------|--------------------------|
| `parse(text)`           | `parse(text)`            |
| `walk(node, visitor)`   | `walk(node, visitor)`    |
| `format(rule)`          | `format(rule)`           |
| `format_ast`, `format_condition`, `format_action`, `format_path`, `format_expr` | `formatAst`, `formatCondition`, `formatAction`, `formatPath`, `formatExpr` |
| `engine.dry_run(entity, deep_copy=True)` | `engine.dryRun(entity, { deepCopy: true })` |
| `detect_conflicts(rules, mode="all_match")` | `detectConflicts(rules, { mode: "all_match" })` |
| `validate(rule, resolver, severity_overrides=…)` | `validate(rule, resolver, { severityOverrides: … })` |
| `builders.eq`, `builders.neq`, `builders.in_`, `builders.not_in` | `builders.eq`, `builders.neq`, `builders.inOp`, `builders.notIn` |
| `builders.and_`, `builders.or_`, `builders.not_` | `builders.and`, `builders.or`, `builders.not` |
| `builders.set_`, `builders.workflow_call`, `builders.ret` | `builders.set_`, `builders.workflowCall`, `builders.ret` |
| `builders.float_lit`, `builders.int_lit` | `builders.floatLit`, `builders.intLit` |
| `BaseResolver.check_path`/`check_assignment`/`check_comparison`/`check_workflow_call` | `BaseResolver.checkPath`/`checkAssignment`/`checkComparison`/`checkWorkflowCall` |
| `grammar_reference()` | `grammarReference()` |
| `DryRunResult.matched_rules`, `.executed_actions`, `.final_entity` | `DryRunResult.matchedRules`, `.executedActions`, `.finalEntity` |

Semantic behavior (operator precedence, canonical formatting, conflict detection, diff structure) is identical across runtimes and enforced by `spec/feature-cases/` fixtures that run in both.

## Parity notes

- Python distinguishes `int` from `float` at runtime; TypeScript has only `number`. `lit(3)` and `lit(3.0)` both produce `literalType: "int"` in TS. For explicit float semantics with cross-runtime parity use `builders.floatLit(3)`.
- Python's list-equality semantics for scalar-vs-list comparison (any-satisfies) are matched in the TS runtime. Deep-equality semantics match via `node:util.isDeepStrictEqual`.

## License

MIT
