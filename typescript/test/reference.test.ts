import { describe, expect, test } from "vitest";
import { grammarReference, parse } from "../src/index.js";

describe("grammar reference", () => {
  test("returns a non-empty string", () => {
    const text = grammarReference();
    expect(typeof text).toBe("string");
    expect(text.length).toBeGreaterThan(500);
  });

  test("contains major sections", () => {
    const text = grammarReference();
    for (const heading of [
      "Rule structure",
      "Condition operators",
      "Path access",
      "Literals",
      "Built-in functions",
      "Assignment",
      "Workflow calls",
    ]) {
      expect(text).toContain(heading);
    }
  });

  test("lists core operators", () => {
    const text = grammarReference();
    for (const op of [
      "==", "!=", "<=", ">=",
      "and", "or", "not",
      "in", "contains",
      "startswith", "endswith", "matches",
      "contains_any", "contains_all",
      "exists", "is_empty",
      "?.", "??",
    ]) {
      expect(text).toContain(op);
    }
  });

  test("every rule example parses", () => {
    const text = grammarReference();
    const blocks = [...text.matchAll(/```\n([\s\S]*?)\n```/g)].map((m) => m[1]);
    const ruleBlocks = blocks.filter((b) => b.includes("=>") && !b.includes("<"));
    expect(ruleBlocks.length).toBeGreaterThanOrEqual(5);

    for (const block of ruleBlocks) {
      for (const line of block.split("\n")) {
        const rule = line.trim();
        if (!rule.includes("=>")) continue;
        expect(() => parse(rule), `example failed to parse: ${rule}`).not.toThrow();
      }
    }
  });
});
