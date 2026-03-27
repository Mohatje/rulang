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
