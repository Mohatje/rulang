import { describe, expect, test } from "vitest";
import {
  builders,
  format,
  parse,
  type And,
  type Comparison,
  type Literal,
  type Not,
  type Or,
  type PathRef,
  type Rule,
  type SetAction,
  type Compound,
} from "../src/index.js";

const {
  and,
  binary,
  compound,
  contains,
  containsAll,
  containsAny,
  endswith,
  eq,
  exists,
  fn,
  gt,
  gte,
  inOp,
  isEmpty,
  lit,
  lt,
  lte,
  matches,
  neq,
  not,
  notContains,
  notIn,
  nullCoalesce,
  or,
  pathOf,
  pathref,
  ret,
  rule,
  set_,
  startswith,
  unary,
  workflowCall,
  workflowExpr,
} = builders;

describe("pathOf", () => {
  test("positional parts", () => {
    const p = pathOf("entity", "a", "b");
    expect(p.root).toBe("entity");
    expect(p.segments.filter((s) => s.kind === "field").map((s) => (s as { name: string }).name)).toEqual(["a", "b"]);
  });
  test("dotted string", () => {
    const p = pathOf("entity.a.b");
    expect(p.root).toBe("entity");
  });
  test("int index", () => {
    const p = pathOf("entity", "items", 0, "name");
    const idx = p.segments.find((s) => s.kind === "index")!;
    expect((idx as { expr: Literal }).expr.value).toBe(0);
  });
  test("null-safe dotted", () => {
    const p = pathOf("entity.a?.b");
    expect(p.segments.some((s) => s.kind === "nullSafeField")).toBe(true);
  });
});

describe("lit", () => {
  const cases: Array<[unknown, string]> = [
    [null, "none"],
    [true, "bool"],
    [42, "int"],
    [3.14, "float"],
    ["hi", "string"],
  ];
  for (const [value, t] of cases) {
    test(`infers ${t}`, () => {
      expect(lit(value).literalType).toBe(t);
    });
  }
  test("list with mixed types", () => {
    const l = lit([1, "two", true]);
    expect(l.literalType).toBe("list");
    const items = l.value as Literal[];
    expect(items[0].literalType).toBe("int");
    expect(items[1].literalType).toBe("string");
    expect(items[2].literalType).toBe("bool");
  });
});

describe("expression builders", () => {
  test("pathref from string", () => {
    const p = pathref("entity.a") as PathRef;
    expect(p.path.root).toBe("entity");
  });
  test("fn call", () => {
    const f = fn("lower", pathref("entity.name"));
    expect(f.name).toBe("lower");
    expect(f.args).toHaveLength(1);
  });
  test("binary + unary", () => {
    expect(binary(pathref("entity.x"), "+", 1).op).toBe("+");
    expect(unary(pathref("entity.x")).type).toBe("unary");
  });
  test("binary rejects invalid op", () => {
    expect(() => binary(1, "**" as never, 2)).toThrow();
  });
  test("nullCoalesce", () => {
    expect(nullCoalesce(pathref("entity.a"), lit("default")).type).toBe("nullCoalesce");
  });
  test("workflowExpr", () => {
    expect(workflowExpr("score", pathref("entity.id")).name).toBe("score");
  });
});

describe("comparison builders", () => {
  const cases: Array<[(l: unknown, r: unknown) => Comparison, string]> = [
    [eq, "=="],
    [neq, "!="],
    [lt, "<"],
    [gt, ">"],
    [lte, "<="],
    [gte, ">="],
    [inOp, "in"],
    [notIn, "not in"],
    [contains, "contains"],
    [notContains, "not contains"],
    [startswith, "startswith"],
    [endswith, "endswith"],
    [matches, "matches"],
    [containsAny, "contains_any"],
    [containsAll, "contains_all"],
  ];
  for (const [f, op] of cases) {
    test(`op ${op}`, () => {
      expect(f(pathref("entity.x"), lit(1)).op).toBe(op);
    });
  }
});

describe("existence", () => {
  test("exists", () => expect(exists(pathref("entity.x")).kind).toBe("exists"));
  test("isEmpty", () => expect(isEmpty(pathref("entity.x")).kind).toBe("is_empty"));
});

describe("logical", () => {
  test("and two args", () => {
    const c = and(eq(pathref("entity.a"), 1), eq(pathref("entity.b"), 2));
    expect((c as And).type).toBe("and");
  });
  test("and three args left-associative", () => {
    const a = eq(pathref("entity.a"), 1);
    const b = eq(pathref("entity.b"), 2);
    const c = eq(pathref("entity.c"), 3);
    const combined = and(a, b, c) as And;
    expect(combined.type).toBe("and");
    expect((combined.left as And).type).toBe("and");
    expect(combined.right).toBe(c);
  });
  test("and requires 2+", () => {
    expect(() => and(eq(1, 1))).toThrow();
  });
  test("or and not", () => {
    expect((or(eq(1, 1), eq(2, 2)) as Or).type).toBe("or");
    expect((not(eq(1, 1)) as Not).type).toBe("not");
  });
});

describe("action builders", () => {
  test("set with string path", () => {
    const s = set_("entity.y", 42) as SetAction;
    expect(s.type).toBe("set");
    expect(s.path.root).toBe("entity");
  });
  test("compound", () => {
    const c = compound("entity.count", "+=", 1) as Compound;
    expect(c.op).toBe("+=");
  });
  test("compound rejects invalid op", () => {
    expect(() => compound("entity.x", "**=" as never, 1)).toThrow();
  });
  test("workflowCall", () => {
    const w = workflowCall("notify", pathref("entity.email"));
    expect(w.name).toBe("notify");
  });
  test("ret", () => {
    expect(ret("done").type).toBe("return");
  });
});

describe("rule builder", () => {
  test("constructs a Rule", () => {
    const r = rule(eq(pathref("entity.age"), 18), [set_("entity.adult", true)]);
    expect(r.type).toBe("rule");
  });
  test("populates reads and writes", () => {
    const r = rule(
      and(gte(pathref("entity.age"), 18), eq(pathref("entity.status"), "active")),
      [set_("entity.adult", true)],
    );
    expect(r.reads.has("entity.age")).toBe(true);
    expect(r.reads.has("entity.status")).toBe(true);
    expect(r.writes.has("entity.adult")).toBe(true);
  });
  test("tracks workflow calls", () => {
    const r = rule(eq(pathref("entity.x"), 1), [workflowCall("notify", pathref("entity.email"))]);
    expect(r.workflowCalls.has("notify")).toBe(true);
  });
});

describe("round-trip", () => {
  test("format of built rule produces expected text", () => {
    const r = rule(eq(pathref("entity.age"), 18), [set_("entity.adult", true)]);
    expect(format(r)).toBe("entity.age == 18 => entity.adult = true");
  });

  test("format → parse → format is idempotent", () => {
    const r = rule(gt(binary(pathref("entity.x"), "+", 1), 5), [ret(lit("hi"))]);
    const once = format(r);
    const twice = format(parse(once));
    expect(once).toBe(twice);
  });
});
