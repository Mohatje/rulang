/**
 * End-to-end integration tests for the new API surface (proposals 1-5, 7, 8).
 *
 * Exercises the full flow: builders → format → parse → validate → dry-run,
 * plus conflict detection across rule sets.
 */

import { describe, expect, test } from "vitest";
import {
  BaseResolver,
  RuleEngine,
  builders,
  detectConflicts,
  format,
  parse,
  pathToString,
  validate,
  type Diagnostic,
  type Path,
  type PathInfo,
} from "../src/index.js";

const {
  and,
  compound,
  eq,
  gt,
  gte,
  lit,
  pathref,
  ret,
  rule,
  set_,
  workflowCall,
} = builders;

describe("API integration", () => {
  test("build → format → reparse → validate → dry-run", () => {
    const r = rule(
      and(gte(pathref("entity.age"), 18), eq(pathref("entity.status"), lit("active"))),
      [set_("entity.adult", true)],
    );

    const text = format(r);
    expect(text).toBe("entity.age >= 18 and entity.status == 'active' => entity.adult = true");

    const reparsed = parse(text);
    expect(reparsed.reads).toEqual(r.reads);
    expect(reparsed.writes).toEqual(r.writes);

    expect(validate(reparsed, new BaseResolver())).toEqual([]);

    const engine = new RuleEngine();
    engine.addRules(text);
    const result = engine.dryRun({ age: 25, status: "active", adult: false });
    expect((result.finalEntity as { adult: boolean }).adult).toBe(true);
    expect(result.diff.adult).toEqual([false, true]);
  });

  test("schema-aware validation with custom resolver", () => {
    class SchemaResolver extends BaseResolver {
      static KNOWN = new Set(["entity.age", "entity.status", "entity.adult"]);
      static WRITABLE = new Set(["entity.adult"]);

      override checkPath(path: Path): PathInfo {
        const p = pathToString(path, { normalizeEntity: "entity", includeIndices: false });
        if (!SchemaResolver.KNOWN.has(p)) return { exists: false };
        return { exists: true, writable: SchemaResolver.WRITABLE.has(p) };
      }
    }

    const typos = validate(
      "entity.age >= 18 and entity.stauts == 'active' => entity.adult = true",
      new SchemaResolver(),
    );
    expect(typos.some((d: Diagnostic) => d.code === "rulang.unknown_path")).toBe(true);

    const readOnly = validate(
      "entity.age >= 18 => entity.status = 'active'",
      new SchemaResolver(),
    );
    expect(readOnly.some((d: Diagnostic) => d.code === "rulang.path_not_writable")).toBe(true);
  });

  test("conflict detection across builder-built rules", () => {
    const a = rule(eq(pathref("entity.x"), 1), [set_("entity.y", lit("a"))]);
    const b = rule(eq(pathref("entity.x"), 1), [set_("entity.y", lit("b"))]);
    const conflicts = detectConflicts([a, b]);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].kind).toBe("contradiction");
  });

  test("round-trip preserves semantic equivalence", () => {
    const built = rule(
      gt(pathref("entity.score"), 100),
      [compound("entity.bonus", "+=", 10), ret(lit("rewarded"))],
    );

    const e1 = new RuleEngine();
    e1.addRules(format(built));
    const entity1 = { score: 150, bonus: 0 };
    expect(e1.evaluate(entity1)).toBe("rewarded");

    const e2 = new RuleEngine();
    e2.addRules(format(parse(format(built))));
    const entity2 = { score: 150, bonus: 0 };
    expect(e2.evaluate(entity2)).toBe("rewarded");

    expect(entity1).toEqual({ score: 150, bonus: 10 });
    expect(entity1).toEqual(entity2);
  });

  test("conflict detection + dry-run cooperate", () => {
    const rulesText = [
      "entity.x == 1 => entity.y = 'a'",
      "entity.x == 1 => entity.y = 'b'",
    ];
    const conflicts = detectConflicts(rulesText, { mode: "all_match" });
    expect(conflicts.some((c) => c.kind === "contradiction")).toBe(true);

    const engine = new RuleEngine("all_match");
    engine.addRules(rulesText);
    const result = engine.dryRun({ x: 1, y: "" });
    expect(["a", "b"]).toContain((result.finalEntity as { y: string }).y);
  });

  test("validate with severity overrides", () => {
    class UnknownPath extends BaseResolver {
      override checkPath(): PathInfo { return { exists: false }; }
    }
    const result = validate(
      "entity.missing == 1 => entity.unknown = 2",
      new UnknownPath(),
      { severityOverrides: { "rulang.unknown_path": "warning" } },
    );
    expect(result.length).toBeGreaterThanOrEqual(2);
    for (const d of result) {
      if (d.code === "rulang.unknown_path") expect(d.severity).toBe("warning");
    }
  });

  test("builders + workflow call", () => {
    const r = rule(
      eq(pathref("entity.trigger"), true),
      [workflowCall("notify", pathref("entity.email"))],
    );
    expect(r.workflowCalls.has("notify")).toBe(true);

    const text = format(r);
    const engine = new RuleEngine();
    engine.addRules(text);

    const calls: string[] = [];
    const notify = (_entity: unknown, email: string) => { calls.push(email); };

    const result = engine.dryRun(
      { trigger: true, email: "a@b.com" },
      { workflows: { notify } },
    );
    expect(calls).toEqual(["a@b.com"]);
    expect(result.returned).toBe(true);
  });

  test("validation + conflict detection compose", () => {
    class Schema extends BaseResolver {
      override checkPath(path: Path): PathInfo {
        const p = pathToString(path, { normalizeEntity: "entity", includeIndices: false });
        return { exists: p === "entity.x" || p === "entity.y" };
      }
    }

    const rules = [
      "entity.x == 1 => entity.y = 'a'",
      "entity.x == 1 => entity.y = 'b'",
      "entity.unknown == 1 => entity.y = 'c'",
    ];

    const conflicts = detectConflicts(rules);
    expect(conflicts.some((c) => c.kind === "contradiction")).toBe(true);

    const diagnostics = validate(rules[2], new Schema());
    expect(diagnostics.some((d: Diagnostic) => d.code === "rulang.unknown_path")).toBe(true);
  });
});
