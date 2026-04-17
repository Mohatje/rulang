import { describe, expect, test } from "vitest";
import { format, formatAst, parse, RuleSyntaxError } from "../src/index.js";

describe("canonical formatter", () => {
  const cases: Array<[string, string]> = [
    ["entity.x==1=>entity.y=2", "entity.x == 1 => entity.y = 2"],
    ["entity.x   ==   1  =>  entity.y   =  2", "entity.x == 1 => entity.y = 2"],
    ["entity.x == 1 => entity.a=1;entity.b=2", "entity.x == 1 => entity.a = 1; entity.b = 2"],
    ['entity.x == "hi" => entity.y = 1', "entity.x == 'hi' => entity.y = 1"],
    ["entity.x == True => entity.y = False", "entity.x == true => entity.y = false"],
    ["entity.x == null => entity.y = None", "entity.x == none => entity.y = none"],
    ["entity.x starts_with 'a' => entity.y = 1", "entity.x startswith 'a' => entity.y = 1"],
    ["entity.x ends_with 'a' => entity.y = 1", "entity.x endswith 'a' => entity.y = 1"],
  ];
  for (const [input, expected] of cases) {
    test(`formats: ${input}`, () => {
      expect(format(input)).toBe(expected);
    });
  }
});

describe("idempotence", () => {
  const samples = [
    "entity.x == 1 => entity.y = 2",
    "entity.a and entity.b => entity.c = 'hi'",
    "entity.x == 1 or entity.y == 2 => entity.z = true",
    "not entity.x == 1 => entity.y = 2",
    "entity.x >= 18 and entity.s == 'ok' => entity.r = true",
    "entity.items[0].name == 'foo' => entity.hit = true",
    "entity.x + 1 * 2 == 3 => entity.y = 1",
    "(entity.x + 1) * 2 == 4 => entity.y = 1",
    "entity.x ?? 0 == 5 => entity.y = 1",
    "lower(entity.name) == 'bob' => entity.y = 1",
    'workflow("log", entity.id) => entity.y = 1',
    "entity.x in [1, 2, 3] => entity.y = 1",
    "entity.x not in [1, 2] => entity.y = 1",
    "entity.x exists => entity.y = 1",
    "entity.x is_empty => entity.y = 1",
    "entity.x == 1 => entity.count += 1",
    "entity.x == 1 => ret 'done'",
  ];
  for (const text of samples) {
    test(`idempotent: ${text}`, () => {
      const once = format(text);
      expect(format(once)).toBe(once);
    });
  }
});

describe("round-trip preserves structure", () => {
  const samples = [
    "entity.age >= 18 => entity.adult = true",
    "entity.x == 1 or entity.y == 2 and entity.z == 3 => entity.r = 'hit'",
    "not (entity.a or entity.b) => entity.x = 1",
    "(entity.a or entity.b) and entity.c => entity.x = 1",
    "entity.items[-1].price == 20 => ret true",
    "entity.x ?? 'default' == 'default' => entity.y = 1",
    "entity.a?.b?.c exists => entity.r = 1",
  ];
  for (const text of samples) {
    test(`round-trip: ${text}`, () => {
      const original = parse(text);
      const reparsed = parse(format(text));
      expect(stripSpans(original)).toEqual(stripSpans(reparsed));
    });
  }
});

describe("precedence & parentheses", () => {
  test("and binds tighter than or — no redundant parens", () => {
    const out = format("entity.a or entity.b and entity.c => entity.r = 1");
    expect(out).toBe("entity.a == true or entity.b == true and entity.c == true => entity.r = 1");
  });

  test("parens preserved for or under and", () => {
    const out = format("(entity.a or entity.b) and entity.c => entity.r = 1");
    expect(out).toContain("(entity.a == true or entity.b == true) and");
  });

  test("mul binds tighter than add", () => {
    const out = format("entity.x == entity.a + entity.b * 2 => entity.y = 1");
    expect(out).toBe("entity.x == entity.a + entity.b * 2 => entity.y = 1");
  });

  test("parens preserved for add under mul", () => {
    const out = format("entity.x == (entity.a + entity.b) * 2 => entity.y = 1");
    expect(out).toContain("(entity.a + entity.b) * 2");
  });

  test("not wraps and in parens", () => {
    const out = format("not (entity.a and entity.b) => entity.r = 1");
    expect(out).toContain("not (entity.a == true and entity.b == true)");
  });
});

describe("strings", () => {
  test("embedded single quote escaped", () => {
    const rule = parse('entity.x == "it\'s" => entity.y = 1');
    expect(format(rule)).toBe("entity.x == 'it\\'s' => entity.y = 1");
  });

  test("backslash escaped", () => {
    const rule = parse(String.raw`entity.x == 'a\\b' => entity.y = 1`);
    expect(format(rule)).toContain("'a\\\\b'");
  });

  test("newline escaped back", () => {
    const rule = parse("entity.x == 'hi\\nworld' => entity.y = 1");
    expect(format(rule)).toContain("'hi\\nworld'");
  });
});

describe("numbers", () => {
  test("int no trailing zero", () => {
    expect(format("entity.x == 5 => entity.y = 1")).toBe("entity.x == 5 => entity.y = 1");
  });
  test("float has decimal", () => {
    expect(format("entity.x == 3.14 => entity.y = 1")).toContain("3.14");
  });
});

describe("API", () => {
  test("accepts AST", () => {
    const rule = parse("entity.x == 1 => entity.y = 2");
    expect(format(rule)).toBe("entity.x == 1 => entity.y = 2");
  });

  test("formatAst alias", () => {
    const rule = parse("entity.x == 1 => entity.y = 2");
    expect(formatAst(rule)).toBe(format(rule));
  });

  test("propagates syntax errors", () => {
    expect(() => format("entity.x ===")).toThrow(RuleSyntaxError);
  });

  test("custom entity name preserved", () => {
    const out = format("shipment.weight > 100 => shipment.heavy = true", "shipment");
    expect(out).toBe("shipment.weight > 100 => shipment.heavy = true");
  });
});

function stripSpans(value: unknown): unknown {
  if (value === null || value === undefined) return value;
  if (value instanceof Set) return new Set([...value].map(stripSpans));
  if (Array.isArray(value)) return value.map(stripSpans);
  if (typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      if (k === "span" || k === "source") continue;
      out[k] = stripSpans(v);
    }
    return out;
  }
  return value;
}
