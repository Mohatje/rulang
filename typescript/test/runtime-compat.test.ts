import { describe, expect, test } from "vitest";
import {
  RuleEngine,
  Workflow,
} from "../src/index.js";

describe("runtime compatibility", () => {
  test("supports negative indices in paths", () => {
    const engine = new RuleEngine();
    engine.addRules("entity.items[-1].price == 20 => ret true");

    expect(
      engine.evaluate({ items: [{ price: 10 }, { price: 20 }] }),
    ).toBe(true);
  });

  test("uses banker's rounding semantics", () => {
    const engine = new RuleEngine();
    engine.addRules("round(entity.price, 2) == 99.98 => ret true");

    expect(engine.evaluate({ price: 99.985 })).toBe(true);
  });

  test("matches Python float rounding for decimal tie cases", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "round(entity.a, 2) == 2.67 => ret true",
      "round(entity.b, 2) == 1.0 => ret true",
      "round(entity.c, -2) == 1400 => ret true",
    ]);

    expect(
      engine.evaluate({
        a: 2.675,
        b: 1.005,
        c: 1350,
      }),
    ).toBe(true);
  });

  test("treats class instances as truthy while keeping empty dict-like objects falsy", () => {
    class User {}

    const truthyEngine = new RuleEngine();
    truthyEngine.addRules("bool(entity.user) == true => ret true");

    const falsyEngine = new RuleEngine();
    falsyEngine.addRules("bool(entity.user) == false => ret true");

    expect(truthyEngine.evaluate({ user: new User() })).toBe(true);
    expect(truthyEngine.evaluate({ user: new Date("2024-01-01T00:00:00Z") })).toBe(true);
    expect(falsyEngine.evaluate({ user: {} })).toBe(true);
  });

  test("rebuilds dependency order when workflow metadata is supplied after inspection", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.ready == true => ret entity.value",
      "true => workflow('mark_ready')",
    ]);

    expect(engine.getExecutionOrder()).toEqual([0, 1]);

    const result = engine.evaluate(
      { ready: false, value: 7 },
      {
        mark_ready: new Workflow({
          fn: (entity) => {
            (entity as { ready: boolean }).ready = true;
          },
          writes: ["entity.ready"],
        }),
      },
    );

    expect(result).toBe(7);
    expect(engine.getExecutionOrder()).toEqual([0, 1]);
  });

  test("supports workflow wrappers and list compound assignment", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "entity.email is_empty => entity.errors += ['Email is required']",
      "entity.errors contains 'Email is required' => workflow('mark_invalid')",
    ]);

    const workflows = {
      mark_invalid: new Workflow({
        fn: (entity) => {
          (entity as { valid: boolean }).valid = false;
        },
        reads: ["entity.errors"],
        writes: ["entity.valid"],
      }),
    };

    const entity = { email: "", errors: [], valid: true };
    engine.evaluate(entity, workflows);

    expect(entity.errors).toEqual(["Email is required"]);
    expect(entity.valid).toBe(false);
  });
});
