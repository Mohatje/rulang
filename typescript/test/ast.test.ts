import { describe, expect, test } from "vitest";
import {
  parse,
  walk,
  pathToString,
  ruleLiterals,
  RuleSyntaxError,
  type Comparison,
  type Existence,
  type And,
  type Not,
  type PathRef,
  type Literal,
  type FunctionCall,
  type Binary,
  type NullCoalesce,
  type Unary,
  type WorkflowCallExpr,
  type SetAction,
  type Compound,
  type WorkflowCallAction,
  type Return,
  type FieldSegment,
  type NullSafeFieldSegment,
  type IndexSegment,
} from "../src/index.js";

describe("parse() returns a Rule", () => {
  test("simple rule with comparison and set action", () => {
    const rule = parse("entity.age >= 18 => entity.isAdult = true");
    expect(rule.type).toBe("rule");
    const cond = rule.condition as Comparison;
    expect(cond.type).toBe("comparison");
    expect(cond.op).toBe(">=");
    expect(rule.actions).toHaveLength(1);
    expect(rule.actions[0].type).toBe("set");
  });

  test("throws RuleSyntaxError on invalid rule", () => {
    expect(() => parse("entity.x ===")).toThrow(RuleSyntaxError);
  });
});

describe("spans populated from source", () => {
  test("every node has a valid span", () => {
    const rule = parse("entity.age >= 18 => entity.adult = true");
    const spans: Array<{ start: number; end: number; line: number; column: number }> = [];
    walk(rule, (n) => {
      const s = (n as { span?: { start: number; end: number; line: number; column: number } }).span;
      if (s) spans.push(s);
    });
    expect(spans.length).toBeGreaterThan(0);
    for (const span of spans) {
      expect(span.start).toBeGreaterThanOrEqual(0);
      expect(span.end).toBeGreaterThanOrEqual(span.start);
      expect(span.line).toBeGreaterThanOrEqual(1);
      expect(span.column).toBeGreaterThanOrEqual(1);
    }
  });

  test("rule span covers source substring", () => {
    const source = "entity.age >= 18 => entity.adult = true";
    const rule = parse(source);
    expect(rule.span).toBeDefined();
    const s = rule.span!;
    expect(source.slice(s.start, s.end).startsWith("entity.age")).toBe(true);
  });
});

describe("condition tree", () => {
  test("and/or/not with parens", () => {
    const rule = parse("not (entity.x == 1 and (entity.y == 2 or entity.z == 3)) => entity.out = 1");
    const n = rule.condition as Not;
    expect(n.type).toBe("not");
    const inner = n.inner as And;
    expect(inner.type).toBe("and");
    expect(inner.left.type).toBe("comparison");
    expect(inner.right.type).toBe("or");
  });
});

describe("comparison operators", () => {
  const cases: Array<[string, string]> = [
    ["entity.x == 1 => entity.y = 1", "=="],
    ["entity.x != 1 => entity.y = 1", "!="],
    ["entity.x < 1 => entity.y = 1", "<"],
    ["entity.x > 1 => entity.y = 1", ">"],
    ["entity.x <= 1 => entity.y = 1", "<="],
    ["entity.x >= 1 => entity.y = 1", ">="],
    ["entity.x in [1, 2] => entity.y = 1", "in"],
    ["entity.x not in [1, 2] => entity.y = 1", "not in"],
    ["entity.x contains 'a' => entity.y = 1", "contains"],
    ["entity.x not contains 'a' => entity.y = 1", "not contains"],
    ["entity.x startswith 'a' => entity.y = 1", "startswith"],
    ["entity.x endswith 'a' => entity.y = 1", "endswith"],
    ["entity.x matches 'a' => entity.y = 1", "matches"],
    ["entity.x contains_any [1] => entity.y = 1", "contains_any"],
    ["entity.x contains_all [1] => entity.y = 1", "contains_all"],
  ];
  for (const [src, op] of cases) {
    test(`op ${op}`, () => {
      const rule = parse(src);
      expect((rule.condition as Comparison).op).toBe(op);
    });
  }
});

describe("existence", () => {
  test("exists", () => {
    const rule = parse("entity.x exists => entity.y = 1");
    const c = rule.condition as Existence;
    expect(c.type).toBe("existence");
    expect(c.kind).toBe("exists");
  });
  test("is_empty", () => {
    const rule = parse("entity.x is_empty => entity.y = 1");
    const c = rule.condition as Existence;
    expect(c.kind).toBe("is_empty");
  });
});

describe("literal types", () => {
  const cases: Array<[string, string, unknown]> = [
    ["entity.x == 42 => entity.y = 1", "int", 42],
    ["entity.x == 3.14 => entity.y = 1", "float", 3.14],
    ["entity.x == 'hello' => entity.y = 1", "string", "hello"],
    ["entity.x == true => entity.y = 1", "bool", true],
    ["entity.x == false => entity.y = 1", "bool", false],
    ["entity.x == none => entity.y = 1", "none", null],
  ];
  for (const [src, lt, value] of cases) {
    test(`literal type ${lt}`, () => {
      const rule = parse(src);
      const lit = (rule.condition as Comparison).right as Literal;
      expect(lit.type).toBe("literal");
      expect(lit.literalType).toBe(lt);
      expect(lit.value).toEqual(value);
    });
  }

  test("list literal with mixed types", () => {
    const rule = parse("entity.x in [1, 'two', true] => entity.y = 1");
    const lit = (rule.condition as Comparison).right as Literal;
    expect(lit.literalType).toBe("list");
    const items = lit.value as Literal[];
    expect(items).toHaveLength(3);
    expect(items[0].literalType).toBe("int");
    expect(items[1].literalType).toBe("string");
    expect(items[2].literalType).toBe("bool");
  });
});

describe("paths", () => {
  test("plain dotted fields", () => {
    const rule = parse("entity.a.b.c == 1 => entity.x = 1");
    const left = (rule.condition as Comparison).left as PathRef;
    expect(left.path.root).toBe("entity");
    const names = left.path.segments
      .filter((s): s is FieldSegment => s.kind === "field")
      .map((s) => s.name);
    expect(names).toEqual(["a", "b", "c"]);
  });

  test("null-safe segment", () => {
    const rule = parse("entity.a?.b == 1 => entity.x = 1");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    expect((path.segments[0] as FieldSegment).kind).toBe("field");
    expect((path.segments[1] as NullSafeFieldSegment).kind).toBe("nullSafeField");
    expect((path.segments[1] as NullSafeFieldSegment).name).toBe("b");
  });

  test("index segment with literal", () => {
    const rule = parse("entity.items[0].name == 'foo' => entity.x = 1");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    const idx = path.segments[1] as IndexSegment;
    expect(idx.kind).toBe("index");
    expect((idx.expr as Literal).value).toBe(0);
  });
});

describe("actions", () => {
  test("set action", () => {
    const rule = parse("entity.x == 1 => entity.y = 2");
    expect((rule.actions[0] as SetAction).type).toBe("set");
  });

  test("compound action operators", () => {
    for (const op of ["+=", "-=", "*=", "/="] as const) {
      const rule = parse(`entity.x == 1 => entity.y ${op} 2`);
      const a = rule.actions[0] as Compound;
      expect(a.type).toBe("compound");
      expect(a.op).toBe(op);
    }
  });

  test("workflow call action", () => {
    const rule = parse('entity.x == 1 => workflow("doit", entity.a)');
    const a = rule.actions[0] as WorkflowCallAction;
    expect(a.type).toBe("workflowCallAction");
    expect(a.name).toBe("doit");
    expect(a.args).toHaveLength(1);
  });

  test("return action", () => {
    const rule = parse("entity.x == 1 => ret 'hit'");
    const a = rule.actions[0] as Return;
    expect(a.type).toBe("return");
    expect((a.value as Literal).value).toBe("hit");
  });

  test("multiple actions", () => {
    const rule = parse("entity.x == 1 => entity.a = 1; entity.b = 2; ret 'done'");
    expect(rule.actions).toHaveLength(3);
    expect(rule.actions[0].type).toBe("set");
    expect(rule.actions[1].type).toBe("set");
    expect(rule.actions[2].type).toBe("return");
  });
});

describe("expressions", () => {
  test("function call", () => {
    const rule = parse("lower(entity.name) == 'abc' => entity.y = 1");
    const left = (rule.condition as Comparison).left as FunctionCall;
    expect(left.type).toBe("functionCall");
    expect(left.name).toBe("lower");
    expect(left.args).toHaveLength(1);
  });

  test("binary arithmetic", () => {
    const rule = parse("entity.x + 1 == 10 => entity.y = 1");
    const left = (rule.condition as Comparison).left as Binary;
    expect(left.type).toBe("binary");
    expect(left.op).toBe("+");
  });

  test("null coalesce", () => {
    const rule = parse("entity.x ?? 0 == 5 => entity.y = 1");
    const left = (rule.condition as Comparison).left as NullCoalesce;
    expect(left.type).toBe("nullCoalesce");
  });

  test("unary minus (path)", () => {
    const rule = parse("entity.x == -entity.y => entity.z = 1");
    const right = (rule.condition as Comparison).right as Unary;
    expect(right.type).toBe("unary");
    expect(right.op).toBe("-");
    expect(right.expr.type).toBe("pathRef");
  });

  test("workflow call in expression position", () => {
    const rule = parse('entity.x == workflow("getX", entity.id) => entity.y = 1');
    const right = (rule.condition as Comparison).right as WorkflowCallExpr;
    expect(right.type).toBe("workflowCallExpr");
    expect(right.name).toBe("getX");
  });
});

describe("extractors", () => {
  test("reads / writes", () => {
    const rule = parse("entity.age >= 18 and entity.status == 'active' => entity.adult = true");
    expect(rule.reads).toEqual(new Set(["entity.age", "entity.status"]));
    expect(rule.writes).toEqual(new Set(["entity.adult"]));
    expect(rule.workflowCalls).toEqual(new Set());
  });

  test("compound reads target", () => {
    const rule = parse("entity.x == 1 => entity.count += 1");
    expect(rule.reads.has("entity.count")).toBe(true);
    expect(rule.writes.has("entity.count")).toBe(true);
  });

  test("workflow call names extracted", () => {
    const rule = parse('entity.x == 1 => workflow("notify", entity.email); workflow("log")');
    expect(rule.workflowCalls).toEqual(new Set(["notify", "log"]));
  });

  test("workflow in expression position tracked", () => {
    const rule = parse('workflow("fetch", entity.id) == true => entity.y = 1');
    expect(rule.workflowCalls.has("fetch")).toBe(true);
  });

  test("paths normalized to entity prefix", () => {
    const rule = parse("age >= 18 => adult = true", "entity");
    expect(rule.reads.has("entity.age")).toBe(true);
    expect(rule.writes.has("entity.adult")).toBe(true);
  });

  test("custom entity name", () => {
    const rule = parse("shipment.weight > 100 => shipment.heavy = true", "shipment");
    expect(rule.reads.has("shipment.weight")).toBe(true);
    expect(rule.writes.has("shipment.heavy")).toBe(true);
  });
});

describe("ruleLiterals helper", () => {
  test("returns all literals", () => {
    const rule = parse("entity.x == 1 and entity.y == 'foo' => entity.z = true");
    const lits = ruleLiterals(rule);
    const values = lits.map((l) => l.value);
    expect(values).toContain(1);
    expect(values).toContain("foo");
    expect(values).toContain(true);
  });
});

describe("walk", () => {
  test("visits multiple node types", () => {
    const rule = parse("entity.x + 1 > 5 => entity.y = 'hi'");
    const typesSeen = new Set<string>();
    walk(rule, (n) => {
      typesSeen.add((n as { type: string }).type);
    });
    expect(typesSeen.has("comparison")).toBe(true);
    expect(typesSeen.has("binary")).toBe(true);
    expect(typesSeen.has("pathRef")).toBe(true);
    expect(typesSeen.has("literal")).toBe(true);
  });
});

describe("pathToString", () => {
  test("basic", () => {
    const rule = parse("entity.a.b.c == 1 => entity.x = 1");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    expect(pathToString(path, { normalizeEntity: "entity" })).toBe("entity.a.b.c");
  });

  test("adds entity prefix if missing", () => {
    const rule = parse("a.b == 1 => x = 1", "entity");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    expect(pathToString(path, { normalizeEntity: "entity" })).toBe("entity.a.b");
  });

  test("no normalize", () => {
    const rule = parse("entity.a == 1 => x = 1", "entity");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    expect(pathToString(path, { normalizeEntity: null })).toBe("entity.a");
  });

  test("indices render as [*] by default", () => {
    const rule = parse("entity.items[0].name == 'x' => entity.y = 1");
    const path = ((rule.condition as Comparison).left as PathRef).path;
    const s = pathToString(path, { normalizeEntity: "entity", includeIndices: false });
    expect(s).toContain("[*]");
  });
});
