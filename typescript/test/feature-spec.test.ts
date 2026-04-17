/**
 * Cross-runtime feature spec — format, conflicts, dry_run.
 *
 * Shares JSON fixtures with the Python runtime. Any divergence between
 * Python and TypeScript output for the same case fails one side of CI.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, test } from "vitest";
import {
  RuleEngine,
  detectConflicts,
  format,
  type EvaluationMode,
} from "../src/index.js";

interface FormatCase {
  id: string;
  input: string;
  expected: string;
}

interface ConflictCase {
  id: string;
  mode?: EvaluationMode;
  rules: string[];
  expected: Array<{
    kind: "duplicate" | "contradiction" | "shadowing";
    rule_indices: [number, number];
    fields?: string[];
  }>;
}

interface DryRunCase {
  id: string;
  mode?: EvaluationMode;
  rules: string[];
  input: Record<string, unknown>;
  expected: {
    matched: Array<{ index: number; condition_result: boolean; executed: boolean }>;
    diff: Record<string, [unknown, unknown]>;
    final_entity: unknown;
    returned: unknown;
  };
}

const specDir = resolve(process.cwd(), "..", "spec", "feature-cases");

function loadBundle<T>(name: string): T[] {
  const raw = JSON.parse(readFileSync(resolve(specDir, name), "utf8"));
  return raw.cases as T[];
}

describe("feature spec: format", () => {
  for (const c of loadBundle<FormatCase>("format.json")) {
    test(c.id, () => {
      expect(format(c.input)).toBe(c.expected);
    });
  }
});

describe("feature spec: conflicts", () => {
  for (const c of loadBundle<ConflictCase>("conflicts.json")) {
    test(c.id, () => {
      const result = detectConflicts(c.rules, { mode: c.mode ?? "all_match" });
      expect(result).toHaveLength(c.expected.length);
      for (let i = 0; i < result.length; i++) {
        const got = result[i];
        const want = c.expected[i];
        expect(got.kind).toBe(want.kind);
        expect(Array.from(got.ruleIndices)).toEqual(want.rule_indices);
        if (want.fields !== undefined) {
          expect(Array.from(got.fields)).toEqual(want.fields);
        }
      }
    });
  }
});

describe("feature spec: dry_run", () => {
  for (const c of loadBundle<DryRunCase>("dry_run.json")) {
    test(c.id, () => {
      const engine = new RuleEngine(c.mode ?? "first_match");
      engine.addRules(c.rules);
      const result = engine.dryRun(c.input);

      const gotMatched = result.matchedRules.map((m) => ({
        index: m.index,
        condition_result: m.conditionResult,
        executed: m.executed,
      }));
      expect(gotMatched).toEqual(c.expected.matched);

      expect(result.diff).toEqual(c.expected.diff);
      expect(result.finalEntity).toEqual(c.expected.final_entity);
      expect(result.returned).toEqual(c.expected.returned);
    });
  }
});
