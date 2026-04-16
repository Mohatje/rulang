import { describe, expect, test } from "vitest";
import { RuleEngine } from "../src/index.js";

describe("dry_run: return shape", () => {
  test("returns a DryRunResult", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.y = 2");
    const result = engine.dryRun({ x: 1, y: 0 });
    expect(Array.isArray(result.matchedRules)).toBe(true);
    expect(Array.isArray(result.executedActions)).toBe(true);
    expect(result.diff).toBeDefined();
    expect(result.finalEntity).toBeDefined();
  });
});

describe("dry_run: non-mutating by default", () => {
  test("default deepCopy preserves original", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.y = 99");
    const entity = { x: 1, y: 0 };
    engine.dryRun(entity);
    expect(entity).toEqual({ x: 1, y: 0 });
  });

  test("deepCopy: false mutates", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.y = 99");
    const entity = { x: 1, y: 0 };
    engine.dryRun(entity, { deepCopy: false });
    expect(entity.y).toBe(99);
  });
});

describe("dry_run: matched_rules", () => {
  test("reports condition results and execution flag", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.x > 0 => entity.a = 1",
      "entity.x < 0 => entity.b = 1",
    ]);
    const r = engine.dryRun({ x: 1, a: 0, b: 0 });
    const byIndex = new Map(r.matchedRules.map((m) => [m.index, m]));
    expect(byIndex.get(0)!.conditionResult).toBe(true);
    expect(byIndex.get(0)!.executed).toBe(true);
    expect(byIndex.get(1)!.conditionResult).toBe(false);
    expect(byIndex.get(1)!.executed).toBe(false);
  });

  test("first_match executes only first", () => {
    const engine = new RuleEngine("first_match");
    engine.addRules([
      "entity.x > 0 => entity.a = 1",
      "entity.x > 0 => entity.b = 1",
    ]);
    const r = engine.dryRun({ x: 1, a: 0, b: 0 });
    expect((r.finalEntity as { a: number }).a).toBe(1);
    expect((r.finalEntity as { b: number }).b).toBe(0);
  });
});

describe("dry_run: executed_actions", () => {
  test("records kind and changes for set", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.y = 42");
    const r = engine.dryRun({ x: 1, y: 0 });
    expect(r.executedActions).toHaveLength(1);
    const a = r.executedActions[0];
    expect(a.ruleIndex).toBe(0);
    expect(a.actionKind).toBe("set");
    expect(a.changes).toHaveLength(1);
    expect(a.changes[0].before).toBe(0);
    expect(a.changes[0].after).toBe(42);
  });

  test("compound action reported", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.count += 5");
    const r = engine.dryRun({ x: 1, count: 10 });
    expect(r.executedActions[0].actionKind).toBe("compound");
    expect(r.executedActions[0].changes[0].before).toBe(10);
    expect(r.executedActions[0].changes[0].after).toBe(15);
  });

  test("workflow action reported", () => {
    const engine = new RuleEngine();
    engine.addRules('entity.x == 1 => workflow("bump", entity.id)');
    const bump = (entity: Record<string, unknown>) => {
      entity.bumped = true;
    };
    const r = engine.dryRun({ x: 1, id: 7, bumped: false }, { workflows: { bump } });
    expect(r.executedActions[0].actionKind).toBe("workflow");
    expect(r.executedActions[0].changes.some((c) => c.path === "bumped")).toBe(true);
  });

  test("return action reported with value", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => ret 'hit'");
    const r = engine.dryRun({ x: 1 });
    const a = r.executedActions[0];
    expect(a.actionKind).toBe("return");
    expect(a.returned).toBe("hit");
  });

  test("returned surfaces on result", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => ret 'yes'");
    expect(engine.dryRun({ x: 1 }).returned).toBe("yes");
  });

  test("no match returns null", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 99 => ret 'no'");
    const r = engine.dryRun({ x: 1 });
    expect(r.returned).toBe(null);
    expect(r.matchedRules.every((m) => !m.executed)).toBe(true);
  });
});

describe("dry_run: diff", () => {
  test("aggregate diff covers all changed paths", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.x == 1 => entity.a = 10",
      "entity.a == 10 => entity.b = 20",
    ]);
    const r = engine.dryRun({ x: 1, a: 0, b: 0 });
    expect(r.diff).toEqual({ a: [0, 10], b: [0, 20] });
  });

  test("multiple writes keep original before and latest after", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.x == 1 => entity.a = 10",
      "entity.a == 10 => entity.a = 20",
    ]);
    const r = engine.dryRun({ x: 1, a: 0 });
    expect(r.diff.a).toEqual([0, 20]);
  });

  test("cancelled change drops from diff", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.x == 1 => entity.a = 10",
      "entity.a == 10 => entity.a = 0",
    ]);
    const r = engine.dryRun({ x: 1, a: 0 });
    expect("a" in r.diff).toBe(false);
  });
});

describe("dry_run: final entity & nesting", () => {
  test("final entity reflects run", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.a == 0 => entity.a = 1",
      "entity.a == 1 => entity.b = 2",
    ]);
    const r = engine.dryRun({ a: 0, b: 0 });
    expect(r.finalEntity).toEqual({ a: 1, b: 2 });
  });

  test("nested paths", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.user.name == 'alice' => entity.user.role = 'admin'");
    const r = engine.dryRun({ user: { name: "alice", role: "guest" } });
    expect(r.diff["user.role"]).toEqual(["guest", "admin"]);
  });

  test("list indices", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.items[0].price == 10 => entity.items[0].price = 15");
    const r = engine.dryRun({ items: [{ price: 10 }, { price: 20 }] });
    expect(r.diff["items[0].price"]).toEqual([10, 15]);
  });
});

describe("dry_run: first_match ret stops later", () => {
  test("ret in first_match halts execution", () => {
    const engine = new RuleEngine("first_match");
    engine.addRules([
      "entity.x > 0 => ret 'positive'",
      "entity.x > 0 => entity.extra = 1",
    ]);
    const r = engine.dryRun({ x: 1, extra: 0 });
    expect(r.returned).toBe("positive");
    expect((r.finalEntity as { extra: number }).extra).toBe(0);
    const second = r.matchedRules.find((m) => m.index === 1)!;
    expect(second.executed).toBe(false);
  });
});

describe("dry_run: anyMatched", () => {
  test("true / false", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.x == 1 => entity.y = 1");
    expect(engine.dryRun({ x: 1, y: 0 }).anyMatched).toBe(true);
    expect(engine.dryRun({ x: 0, y: 0 }).anyMatched).toBe(false);
  });
});
