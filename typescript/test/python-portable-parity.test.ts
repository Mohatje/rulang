import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, test } from "vitest";
import { RuleEngine, RuleSyntaxError, parseRule } from "../src/index.js";

type PortableCase =
  | {
      id: string;
      kind: "evaluate";
      mode: "first_match" | "all_match";
      rules: string[];
      input: Record<string, unknown>;
      expected_result: unknown;
      expected_entity?: Record<string, unknown>;
    }
  | {
      id: string;
      kind: "parse";
      rule: string;
      entity_name?: string | null;
      expected: {
        reads: string[];
        writes: string[];
        workflow_calls: string[];
      };
    }
  | {
      id: string;
      kind: "parse_error";
      rule: string;
      entity_name?: string | null;
      expected_error: string;
    };

const casesPath = resolve(process.cwd(), "..", "spec", "generated", "python-portable-cases.json");
const cases = JSON.parse(readFileSync(casesPath, "utf8")) as PortableCase[];

describe("portable python parity corpus", () => {
  for (const parityCase of cases) {
    test(parityCase.id, () => {
      if (parityCase.kind === "evaluate") {
        const engine = new RuleEngine(parityCase.mode);
        engine.addRules(parityCase.rules);
        const entity = structuredClone(parityCase.input);
        const result = engine.evaluate(entity);
        expect(result).toEqual(parityCase.expected_result);
        if (parityCase.expected_entity) {
          expect(entity).toEqual(parityCase.expected_entity);
        }
        return;
      }

      if (parityCase.kind === "parse") {
        const parsed = parseRule(parityCase.rule, parityCase.entity_name ?? "entity");
        expect([...parsed.reads].sort()).toEqual(parityCase.expected.reads);
        expect([...parsed.writes].sort()).toEqual(parityCase.expected.writes);
        expect([...parsed.workflowCalls].sort()).toEqual(parityCase.expected.workflow_calls);
        return;
      }

      expect(() => parseRule(parityCase.rule, parityCase.entity_name ?? "entity")).toThrowError(RuleSyntaxError);
    });
  }
});
