import { describe, expect, test } from "vitest";
import { detectConflicts, parse } from "../src/index.js";

describe("duplicates", () => {
  test("identical rules", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 2",
      "entity.x == 1 => entity.y = 2",
    ]);
    expect(c).toHaveLength(1);
    expect(c[0].kind).toBe("duplicate");
    expect(c[0].ruleIndices).toEqual([0, 1]);
  });

  test("whitespace variants", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 2",
      "entity.x==1=>entity.y=2",
    ]);
    expect(c[0].kind).toBe("duplicate");
  });

  test("quote-style variants", () => {
    const c = detectConflicts([
      "entity.status == 'active' => entity.ok = true",
      `entity.status == "active" => entity.ok = true`,
    ]);
    expect(c[0].kind).toBe("duplicate");
  });

  test("alias operator variants", () => {
    const c = detectConflicts([
      "entity.name starts_with 'A' => entity.y = 1",
      "entity.name startswith 'A' => entity.y = 1",
    ]);
    expect(c[0].kind).toBe("duplicate");
  });

  test("non-duplicates produce no conflicts", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 2",
      "entity.x == 2 => entity.y = 3",
    ]);
    expect(c).toEqual([]);
  });
});

describe("contradictions", () => {
  test("same condition different literal values", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 'a'",
      "entity.x == 1 => entity.y = 'b'",
    ]);
    expect(c).toHaveLength(1);
    expect(c[0].kind).toBe("contradiction");
    expect(c[0].fields).toContain("entity.y");
    expect(c[0].diff["entity.y"]).toEqual([
      ["string", "a"],
      ["string", "b"],
    ]);
  });

  test("multiple fields reported", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.a = 1; entity.b = 2",
      "entity.x == 1 => entity.a = 9; entity.b = 8",
    ]);
    expect(c[0].kind).toBe("contradiction");
    expect(new Set(c[0].fields)).toEqual(new Set(["entity.a", "entity.b"]));
  });

  test("no contradiction when writes agree (no shared paths)", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 1; entity.a = 1",
      "entity.x == 1 => entity.y = 1; entity.b = 2",
    ]);
    expect(c.every((x) => x.kind !== "contradiction")).toBe(true);
  });

  test("ignores non-literal RHS", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = entity.a",
      "entity.x == 1 => entity.y = entity.b",
    ]);
    expect(c.every((x) => x.kind !== "contradiction")).toBe(true);
  });
});

describe("shadowing (first_match)", () => {
  test("detected on identical conditions", () => {
    const c = detectConflicts(
      [
        "entity.x == 1 => entity.a = 1",
        "entity.x == 1 => entity.b = 2",
      ],
      { mode: "first_match" },
    );
    expect(c).toHaveLength(1);
    expect(c[0].kind).toBe("shadowing");
  });

  test("not reported in all_match", () => {
    const c = detectConflicts(
      [
        "entity.x == 1 => entity.a = 1",
        "entity.x == 1 => entity.b = 2",
      ],
      { mode: "all_match" },
    );
    expect(c).toEqual([]);
  });

  test("duplicate supersedes shadowing", () => {
    const c = detectConflicts(
      [
        "entity.x == 1 => entity.y = 2",
        "entity.x == 1 => entity.y = 2",
      ],
      { mode: "first_match" },
    );
    expect(c).toHaveLength(1);
    expect(c[0].kind).toBe("duplicate");
  });
});

describe("inputs", () => {
  test("accepts AST inputs", () => {
    const a = parse("entity.x == 1 => entity.y = 2");
    const b = parse("entity.x == 1 => entity.y = 2");
    const c = detectConflicts([a, b]);
    expect(c[0].kind).toBe("duplicate");
  });

  test("mixed string and AST", () => {
    const ast = parse("entity.x == 1 => entity.y = 2");
    const c = detectConflicts([ast, "entity.x == 1 => entity.y = 2"]);
    expect(c[0].kind).toBe("duplicate");
  });
});

describe("pair coverage", () => {
  test("all pairs reported for triple duplicates", () => {
    const c = detectConflicts([
      "entity.x == 1 => entity.y = 2",
      "entity.x == 1 => entity.y = 2",
      "entity.x == 1 => entity.y = 2",
    ]);
    const pairs = new Set(c.map((x) => JSON.stringify(x.ruleIndices)));
    expect(pairs).toEqual(
      new Set([
        JSON.stringify([0, 1]),
        JSON.stringify([0, 2]),
        JSON.stringify([1, 2]),
      ]),
    );
  });
});
