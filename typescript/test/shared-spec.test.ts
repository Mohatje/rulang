import { readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { describe, expect, test } from "vitest";
import {
  EvaluationError,
  RuleEngine,
  RuleSyntaxError,
  parseRule,
} from "../src/index.js";

type ParseOnlyCase = {
  id: string;
  parse_only: true;
  rule: string;
  expected: {
    error_type?: string;
    reads?: string[];
    writes?: string[];
    workflow_calls?: string[];
  };
};

type EvaluationCase = {
  id: string;
  mode?: "first_match" | "all_match";
  rules: string[];
  input: Record<string, unknown>;
  expected: {
    result: unknown;
    entity: Record<string, unknown>;
    execution_order?: number[];
  };
};

const specDir = resolve(process.cwd(), "..", "spec", "cases");
const cases = readdirSync(specDir)
  .filter((file) => file.endsWith(".json"))
  .sort()
  .map((file) =>
    JSON.parse(readFileSync(join(specDir, file), "utf8")) as ParseOnlyCase | EvaluationCase,
  );

describe("shared spec", () => {
  for (const testCase of cases) {
    test(testCase.id, () => {
      if ("parse_only" in testCase && testCase.parse_only) {
        if (testCase.expected.error_type) {
          expect(() => parseRule(testCase.rule)).toThrowError(
            testCase.expected.error_type === "RuleSyntaxError" ? RuleSyntaxError : EvaluationError,
          );
          return;
        }

        const parsed = parseRule(testCase.rule);
        expect([...parsed.reads].sort()).toEqual(testCase.expected.reads ?? []);
        expect([...parsed.writes].sort()).toEqual(testCase.expected.writes ?? []);
        expect([...parsed.workflowCalls].sort()).toEqual(testCase.expected.workflow_calls ?? []);
        return;
      }

      const engine = new RuleEngine(testCase.mode ?? "first_match");
      engine.addRules(testCase.rules);
      const entity = structuredClone(testCase.input);
      const result = engine.evaluate(entity);

      expect(result).toEqual(testCase.expected.result);
      expect(entity).toEqual(testCase.expected.entity);

      if (testCase.expected.execution_order) {
        expect(engine.getExecutionOrder()).toEqual(testCase.expected.execution_order);
      }
    });
  }
});
