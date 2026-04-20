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

    const workflows = {
      mark_ready: new Workflow({
        fn: (entity) => {
          (entity as { ready: boolean }).ready = true;
        },
        writes: ["entity.ready"],
      }),
    };

    expect(engine.getExecutionOrder(workflows)).toEqual([1, 0]);
    expect(engine.getDependencyGraph(workflows)).toEqual({ 1: new Set([0]) });

    const result = engine.evaluate(
      { ready: false, value: 7 },
      workflows,
    );

    expect(result).toBe(7);
    expect(engine.getExecutionOrder()).toEqual([0, 1]);
  });

  test("tracks workflow-written dependencies for implicit paths with passed workflows", () => {
    const engine = new RuleEngine("all_match");
    engine.addRules([
      "parameters.computed_load_metric > 1 => parameters.processing_mode = 'expanded'",
      "not (parameters.package_count is_empty) => workflow('calculate_load_metrics')",
    ]);

    const workflows = {
      calculate_load_metrics: new Workflow({
        fn: (entity) => {
          const parameters = (entity as {
            parameters: {
              computed_load_metric?: number;
              computed_load_index?: number;
            };
          }).parameters;
          parameters.computed_load_metric = 1.3;
          parameters.computed_load_index = 13.71;
        },
        reads: [
          "entity.parameters.package_count",
          "entity.parameters.package_length",
          "entity.parameters.package_width",
          "entity.parameters.package_height",
          "entity.parameters.package_weight",
          "entity.parameters.stackable",
          "entity.parameters.packaging_type",
          "entity.parameters.weight_per_unit",
          "entity.shipment.stops",
          "entity.shipment.parameters.vehicle_type",
          "entity.shipment.parameters.vehicle_group",
        ],
        writes: [
          "entity.parameters.computed_load_metric",
          "entity.parameters.computed_load_index",
          "entity.computed_load_metric",
          "entity.computed_load_index",
        ],
      }),
    };

    expect(engine.getExecutionOrder(workflows)).toEqual([1, 0]);
    expect(engine.getDependencyGraph(workflows)).toEqual({ 1: new Set([0]) });

    const entity = {
      parameters: {
        package_count: 3,
        package_length: 130,
        package_width: 110,
        package_height: 100,
        package_weight: 24000,
        stackable: true,
      },
    };

    expect(engine.evaluate(entity, workflows)).toBe(true);
    expect(entity).toEqual({
      parameters: {
        package_count: 3,
        package_length: 130,
        package_width: 110,
        package_height: 100,
        package_weight: 24000,
        stackable: true,
        computed_load_metric: 1.3,
        computed_load_index: 13.71,
        processing_mode: "expanded",
      },
    });
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
